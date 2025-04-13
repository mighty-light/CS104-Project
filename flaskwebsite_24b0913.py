import os, csv, subprocess
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, render_template
from flask import request, send_file
from werkzeug.utils import secure_filename
from datetime import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

TIME_LADDER = ['year', 'month', 'date', 'hour', 'minute', 'second']
FROM_TIME_LADDER = [f"from_{TIME}" for TIME in TIME_LADDER]
TO_TIME_LADDER = [f"to_{TIME}" for TIME in TIME_LADDER]
STRUCTURED_CSV_FOLDER = 'csv'
PARSER_FOLDER = 'Parser'
FILTER_SCRIPT_FOLDER = 'Filter'
IMAGE_FOLDER = 'img'

uploaded_files = []
csv_headers_table = []
rows_csv_table = []


def get_image_path(filepath, extension):
    return os.path.join(IMAGE_FOLDER, f"plot_{os.path.basename(filepath)}.{extension}")

def get_file_data(html_name):
    return [file_data for file_data in uploaded_files if file_data['name'] == request.form.get(html_name)][0]

def get_csv_path_from_data(file_data, filtered=False):
    if not filtered:
        return os.path.join(STRUCTURED_CSV_FOLDER, f"{file_data['name']}_structured.csv")
    return os.path.join(STRUCTURED_CSV_FOLDER, f"filtered_{file_data['name']}_structured.csv")

def get_filter_script(file_data):
    return os.path.join(FILTER_SCRIPT_FOLDER, f"{file_data['type']}_filter.sh")

# Takes advantage of the fact that list comprehensions preserve order of ITERABLE
def find_start_date():
    time_parts = [request.form.get(TIME) for TIME in FROM_TIME_LADDER]
    if "" in time_parts:
        return ""  
    return ":".join(time_parts)

# Takes advantage of the fact that list comprehensions preserve order of ITERABLE
def find_end_date():
    time_parts = [request.form.get(TIME) for TIME in TO_TIME_LADDER]
    if "" in time_parts:
        return ""
    
    return ":".join(time_parts)

@app.route("/")
def main():
    return render_template("main.html", title="Welcome to Log Analysis Platform")

##############################################################
################# UPLOAD FILES ###############################
##############################################################

@app.route("/upload", methods=[ 'GET', 'POST' ])
def upload():
    if request.method == 'POST':
        upload_file()
    return render_template("upload.html", title="Upload Files", file_info=uploaded_files)

def upload_file():
    if 'uploaded_log' not in request.files:
        return False
    
    log = request.files['uploaded_log']
    
    if secure_filename(log.filename) == '':
        return False
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(log.filename))
    log.save(filepath)
    run_bash_validator(filepath, name=secure_filename(log.filename), kind=request.form.get('log_type'))
    return True

# os.path.join will give windows version of the path but we need unix version for WSL
def run_bash_validator(filepath, kind=None, name=None):
    wsl_file_path = filepath.replace("\\", "/")
    validator_path = os.path.join("Validator", f"{kind}_validator.sh").replace("\\", "/")

    bash_script = subprocess.run(
        ["wsl", validator_path, wsl_file_path], capture_output=True, text=True
    )
    
    uploaded_files.append({
        'name' : name,
        'type' : kind,
        'time' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'valid': bash_script.returncode == 0,
        'csv' : False,
    })


################################################################
##################### TABLE DISPLAY ############################
################################################################

@app.route("/table", methods=[ 'GET', 'POST' ])
def table():
    if request.method == 'POST':
        if 'make-csv' in request.form:
            file_data = get_file_data('up_log_file')
            if not file_data['csv']:
                make_structured_csv(file_data)
        
        if 'show-table' in request.form:    
            file_data = get_file_data('csv_file')
            display_table(file_data)

        if 'download-table' in request.form:
            start_date = find_start_date()
            end_date = find_end_date()

            file_data = get_file_data('csv_for_download')
            prepare_filtered_csv_file(start_date, end_date, file_data)
            return download_filtered_table(file_data)

    valid_files = [file_data for file_data in uploaded_files if file_data['valid']]
    has_csv = [file for file in uploaded_files if file['csv']]
    
    return render_template("table.html", title="View Table", file_info=valid_files,
                           has_csv=has_csv, headers=csv_headers_table, rows=rows_csv_table)

def make_structured_csv(file_data):
    os.makedirs(STRUCTURED_CSV_FOLDER, exist_ok=True)
    parser_path = os.path.join(PARSER_FOLDER, f"log_parser_{file_data['type']}.sh").replace("\\", "/")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data['name']).replace("\\", "/")
    subprocess.run(
        ["wsl", parser_path, file_path], capture_output=True, text=True
    )    
    file_data['csv'] = True

# Maybe add a hide table option?
def display_table(file_data):
    csv_path = get_csv_path_from_data(file_data)
    global csv_headers_table
    global rows_csv_table
    with open(csv_path, "r") as file:
        csv_reader = csv.reader(file)
        csv_headers_table = next(csv_reader)
        rows_csv_table = list(csv_reader)

def prepare_filtered_csv_file(start_date, end_date, file_data):
    csv_file_path = get_csv_path_from_data(file_data).replace("\\", "/")
    filtered_csv = get_csv_path_from_data(file_data, filtered=True).replace("\\", "/")
    filter_script = get_filter_script(file_data).replace("\\", "/")

    mode = (start_date != "") + 2 * (end_date != "")

    subprocess.run(
        ["wsl", filter_script, str(mode), csv_file_path, filtered_csv, start_date, end_date], capture_output=True, text=True
    )  


def download_filtered_table(file_data):
    filtered_file_path = get_csv_path_from_data(file_data, filtered=True)
    return send_file(filtered_file_path, as_attachment=True)

### NOTE: Much of the hard coding (if else) can be removed if we use the
### mktime() function of awk that will calculate the time from epoch.
### It will also work with weird date-time choices, e.g., daylight savings.
### NOTE: The apache logs are automatically sorted by date.
### TODO: Add option to sort by some other column? [OPTIONAL]

################################################################
##################### PLOT DISPLAY #############################
################################################################



@app.route("/plots", methods=[ 'GET', 'POST' ])
def plots():
    if 'plot-table' in request.form:
            start_date = find_start_date()
            end_date = find_end_date()

            file_data = get_file_data('csv_for_download')
            prepare_filtered_csv_file(start_date, end_date, file_data)

            filepath = get_csv_path_from_data(file_data, filtered=True)
            file_ext = request.form.get('plt-extension')
            return create_plots(filepath, file_ext, kind=file_data['type'])

    return render_template("plots.html", title="Generate Plots", has_csv = [file for file in uploaded_files if file['csv']])

def create_plots(filepath, extension='jpeg', kind=None):
    
    plot_path = get_image_path(filepath, extension) 
    
    level_state = { 'notice' : 0, 'error' : 0 }
    event_id = { 'E1' : 0, 'E2' : 0, 'E3' : 0, 'E4' : 0, 'E5' : 0, 'E6' : 0 }
    event_times = []
    with open(filepath) as filtered_csv_file:
        reader = csv.DictReader(filtered_csv_file)
        for row in reader:
            level_state[row['Level']] += 1
            event_id[row['EventId']] += 1
            event_times.append(convert_to_datetime(row['Time'], kind='apache'))
            
    if kind == 'apache':
        # Add custom font formatting
        title_font = {'family': 'serif', 'color': 'darkblue', 'weight': 'bold', 'size': 16,}
        plt.subplot(3, 1, 1)
        plt.plot(event_times, range(len(event_times)), "bo-")
        plt.title('Events logged with time', fontdict=title_font)

        plt.subplot(3, 1, 2)
        plt.pie(level_state.values(), labels=level_state.keys())
        plt.title('Level State Distribution', fontdict=title_font)

        plt.subplot(3, 1, 3)
        plt.bar(event_id.keys(), event_id.values())
        plt.title('Event Code Distribution', fontdict=title_font)
        plt.tight_layout()
        
        os.makedirs(IMAGE_FOLDER, exist_ok=True)
        plt.savefig(plot_path)

        # Remove in final version
        plt.show()
     
    return send_file(plot_path, as_attachment=True)


def convert_to_datetime(string, kind=None):
    month_to_number = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    if kind == 'apache':
        date = string.split()
        year = int(date[-1])
        month = month_to_number[date[1]]
        day = int(date[2])
        hrs, mnt, sec = map(int, date[3].split(":"))

        return datetime(year, month, day, hour=hrs, minute=mnt, second=sec)


#################################################################
######## MAYBE ADD CUSTOM INPUT FOR CREATING PLOTS ##############
######## (OR ADD SUPPORT FOR OTHER FILES FIRST)    ##############
######## DRAG AND DROP FUNCTIONALITY               ##############
#################################################################

if __name__ == "__main__":
    app.run(debug=True)