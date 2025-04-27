import numpy as np
import os, csv, subprocess
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, render_template
from flask import request, send_file, send_from_directory
from werkzeug.utils import secure_filename

import matplotlib
matplotlib.use('Agg') # set Agg backend to avoid GUI issues

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
uploaded_files = []

TIME_LADDER = ['year', 'month', 'date', 'hour', 'minute', 'second']
FROM_TIME_LADDER = [f"from_{TIME}" for TIME in TIME_LADDER]
TO_TIME_LADDER = [f"to_{TIME}" for TIME in TIME_LADDER]
STRUCTURED_CSV_FOLDER = 'csv'
VALIDATOR_FOLDER = 'Validator'
PARSER_FOLDER = 'Parser'
FILTER_SCRIPT_FOLDER = 'Filter'
IMAGE_FOLDER = 'img'
SUPPORTED_LOG_FORMATS = ['apache', 'android', 'syslog']


def get_image_path(filepath, extension):
    return os.path.join(IMAGE_FOLDER, f"plot_{os.path.basename(filepath)}.{extension}")

def get_image_name(filepath, extension):
    return f"plot_{os.path.basename(filepath)}.{extension}"

def get_file_data(html_name):
    return [file_data for file_data in uploaded_files if file_data['name'] == request.form.get(html_name)][0]

def get_csv_path_from_data(file_data, filtered=False):
    if not filtered:
        return os.path.join(STRUCTURED_CSV_FOLDER, f"{file_data['name']}_structured.csv")
    return os.path.join(STRUCTURED_CSV_FOLDER, f"filtered_{file_data['name']}_structured.csv")

def get_filter_script(file_data):
    return os.path.join(FILTER_SCRIPT_FOLDER, f"{file_data['type']}_filter.sh")

def get_validator_path(kind):
    return os.path.join(VALIDATOR_FOLDER, f"{kind}_validator.sh")

def find_start_date():
    """Get the FROM DATE for filtering from the form"""
    time_parts = [request.form.get(TIME) for TIME in FROM_TIME_LADDER]
    if "" in time_parts:
        return ""  
    return ":".join(time_parts)

def find_end_date():
    """Get the TO DATE for filtering from the form"""
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

    kind = request.form.get('log_type')
    if kind == 'auto':
        auto_detect_log_type(filepath, name=secure_filename(log.filename))
    else:
        run_bash_validator(filepath, name=secure_filename(log.filename), kind=kind)
    return True

# os.path.join will give windows version of the path but we need unix version for WSL
def run_bash_validator(filepath, kind=None, name=None):
    wsl_file_path = filepath.replace("\\", "/")
    validator_path = get_validator_path(kind).replace('\\', '/')

    bash_script = subprocess.run(
        ["bash", validator_path, wsl_file_path], capture_output=True, text=True
    )
    
    uploaded_files.append({
        'name' : name,
        'type' : kind,
        'time' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'valid': bash_script.returncode == 0,
        'csv' : False,
    })

def auto_detect_log_type(filepath, name=None):
    valid_log_file = False
    file_format = 'auto'
    wsl_file_path = filepath.replace('\\', '/')

    for format in SUPPORTED_LOG_FORMATS:
        validator_path = get_validator_path(format).replace('\\', '/')

        bash_script = subprocess.run(
            ["bash", validator_path, wsl_file_path], capture_output=True, text=True
        )

        if bash_script.returncode == 0:
            valid_log_file = True
            file_format = format
            break
    
    uploaded_files.append({
        'name' : name,
        'type' : file_format,
        'time' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'valid': valid_log_file,
        'csv' : False,
    })
        
    

################################################################
##################### TABLE DISPLAY ############################
################################################################

@app.route("/table", methods=[ 'GET', 'POST' ])
def table():
    table_headings = []
    table_rows = []

    if request.method == 'POST':
        if 'make-csv' in request.form:
            file_data = get_file_data('up_log_file')
            if not file_data['csv']:
                make_structured_csv(file_data)
        
        if 'show-table' in request.form:    
            file_data = get_file_data('csv_file')
            table_headings, table_rows = display_table(file_data)


        if 'download-table' in request.form:
            start_date = find_start_date()
            end_date = find_end_date()

            file_data = get_file_data('csv_for_download')
            prepare_filtered_csv_file(start_date, end_date, file_data)
            return download_filtered_table(file_data)

    valid_files = [file_data for file_data in uploaded_files if file_data['valid']]
    has_csv = [file for file in uploaded_files if file['csv']]
    
    return render_template("table.html", title="View Table", file_info=valid_files,
                           has_csv=has_csv, headers=table_headings, rows=table_rows)

def make_structured_csv(file_data):
    os.makedirs(STRUCTURED_CSV_FOLDER, exist_ok=True)
    parser_path = os.path.join(PARSER_FOLDER, f"log_parser_{file_data['type']}.sh").replace("\\", "/")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data['name']).replace("\\", "/")
    subprocess.run(
        ["bash", parser_path, file_path], capture_output=True, text=True
    )    
    file_data['csv'] = True

def display_table(file_data):
    csv_path = get_csv_path_from_data(file_data)

    with open(csv_path, "r") as file:
        csv_reader = csv.reader(file)
        table_headings = next(csv_reader)
        table_rows = list(csv_reader)

# In case of tame log files like Apache, we can use the following approach
#       header = next(file).strip().split(',')
#       rows = [line.strip().split(',') for line in file]
#       return header, rows

    return table_headings, table_rows

def prepare_filtered_csv_file(start_date, end_date, file_data):
    csv_file_path = get_csv_path_from_data(file_data).replace("\\", "/")
    filtered_csv = get_csv_path_from_data(file_data, filtered=True).replace("\\", "/")
    filter_script = get_filter_script(file_data).replace("\\", "/")

    mode = (start_date != "") + 2 * (end_date != "")

    subprocess.run(
        ["bash", filter_script, str(mode), csv_file_path, filtered_csv, start_date, end_date], capture_output=True, text=True
    )  


def download_filtered_table(file_data):
    filtered_file_path = get_csv_path_from_data(file_data, filtered=True)
    return send_file(filtered_file_path, as_attachment=True)

### NOTE: Much of the hard coding (if else) can be removed if we use the
### mktime() function of awk that will calculate the time from epoch.
### It will also work with weird date-time choices, e.g., daylight savings.

################################################################
##################### PLOT DISPLAY #############################
################################################################

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory('img', filename)


@app.route("/plots", methods=[ 'GET', 'POST' ])
def plots():
    plot_name = None
    if 'plot-table' in request.form:
            start_date = find_start_date()
            end_date = find_end_date()

            file_data = get_file_data('csv_for_download')
            prepare_filtered_csv_file(start_date, end_date, file_data)

            filepath = get_csv_path_from_data(file_data, filtered=True)
            file_ext = request.form.get('plt-extension')
            plot_name = create_plots(filepath, file_ext, kind=file_data['type'])

    return render_template("plots.html", title="Generate Plots", plot_name=plot_name,
                           has_csv = [file for file in uploaded_files if file['csv']])

def create_plots(filepath, extension='jpeg', kind=None):
    
    plot_path = get_image_path(filepath, extension).replace('\\', '/')             
    title_font = {'family': 'serif', 'color': 'darkblue', 'weight': 'bold', 'size': 16,}

    if kind == 'apache':
        draw_apache_plot(filepath, title_font=title_font)
    elif kind == 'android':
        draw_android_plot(filepath, title_font=title_font)
    elif kind == 'syslog':
        draw_syslog_plot(filepath, title_font=title_font)

    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    plt.style.use('fivethirtyeight')
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    return get_image_name(filepath, extension)

def draw_apache_plot(filepath, title_font=None):
    level_state = { 'notice' : 0, 'error' : 0 }
    event_id = { 'E1' : 0, 'E2' : 0, 'E3' : 0, 'E4' : 0, 'E5' : 0, 'E6' : 0 }
    event_times = []
    with open(filepath) as filtered_csv_file:
        next(filtered_csv_file) 
        for line in filtered_csv_file:
            row = line.strip().split(',')
        #     0      1    2      3       4         5
        #   LineId Time Level Content EventId EventTemplate
            level_state[row[2]] += 1
            event_id[row[4]] += 1
            event_times.append(convert_to_datetime(row[1], kind='apache'))

    plt.subplot(3, 1, 1)
    plt.plot(event_times, range(len(event_times)), "bo-")
    plt.title('Events logged with time', fontdict=title_font)

    plt.subplot(3, 1, 2)
    plt.pie(level_state.values(), labels=level_state.keys())
    plt.title('Level State Distribution', fontdict=title_font)

    plt.subplot(3, 1, 3)
    plt.bar(event_id.keys(), event_id.values())
    plt.title('Event Code Distribution', fontdict=title_font)

def draw_android_plot(filepath, title_font=None):
    level_state = {}
    event_times = []
    component = []

    with open(filepath) as filtered_csv_file:
        next(filtered_csv_file) 
        for line in filtered_csv_file:
            row = line.strip().split(',')
        #     0     1     2   3   4    5       6
        #   LineId Date Time Pid Tid Level Component ...   
            date = row[1].split('-')
            date = date[0] + " " + date[1] + " " + row[2].split('.')[0]
            event_times.append(convert_to_datetime(date, kind='android'))
            component.append(row[6])
            level_state.setdefault(row[5], 0)
            level_state[row[5]] += 1

    plt.subplot(3, 1, 1)
    plt.plot(event_times, component, "bo-")
    plt.title('Event Component Over Time', fontdict=title_font)

    plt.subplot(3, 1, 2)
    plt.plot(event_times, range(len(event_times)), "bo-")
    plt.title('Traffic trends', fontdict=title_font)

    plt.subplot(3, 1, 3)
    plt.pie(level_state.values(), labels=level_state.keys())
    plt.title('Level Breakdown ', fontdict=title_font)
    
def draw_syslog_plot(filepath, title_font=None):
    level_state = {'combo' : 0}
    log_src = {}
    event_times = []
    with open(filepath) as filtered_csv_file:
        next(filtered_csv_file) 
        for line in filtered_csv_file:
            row = line.strip().split(',')
        #     0      1    2    3     4       5
        #   LineId Month Date Time Level Component ...
            level_state.setdefault(row[4], 0)
            level_state[row[4]] += 1

            log_src.setdefault(row[5], 0)
            log_src[row[5]] += 1

            event_times.append(convert_to_datetime(" ".join((row[1], row[2], row[3])), kind='syslog'))
    
    plt.subplot(3, 1, 1)
    plt.plot(event_times, range(len(event_times)), "bo-")
    plt.title('Events logged with time', fontdict=title_font)

    plt.subplot(3, 1, 2)
    plt.pie(level_state.values(), labels=level_state.keys())
    plt.title('Level State Distribution', fontdict=title_font)

    plt.subplot(3, 1, 3)
    src, num = [*zip(*most_common(log_src, 5))]
    plt.bar(src, num)
    plt.title('Top Log Sources', fontdict=title_font)

def most_common(dictionary, k):
    return sorted(dictionary.items(), key=lambda x: x[1], reverse=True)[:k]
    
def convert_to_datetime(string, kind=None):
    """Convert the different kinds of date strings from different types of log
    files to a universal format (in this case np.datetime64)"""

    month_to_str = {
        "01": "01", "02": "02", "03": "03", "04": "04",
        "05": "05", "06": "06", "07": "07", "08": "08",
        "09": "09", "10": "10", "11": "11", "12": "12",
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    # Apache logs have day of the week as the second entry while the other logs
    # have it as the first entry, therefore this space-saving hack
    magic_bit = kind == 'apache'

    date = string.split()
    month = month_to_str[date[magic_bit]]
    
    day = date[1+magic_bit].zfill(2)
    hrs, mnt, sec = date[2+magic_bit].split(":")
    # Unnecessary in this implementation but
    # was useful in the earlier versions using datetime
    
    if kind == 'apache':
        year = date[-1]
    elif kind == 'syslog' or kind == 'android':
        year = str(1970)

    return np.datetime64(year + '-' +  month + '-' +  day + 'T' + hrs + ':' + mnt + ':' + sec)


#################################################################
######## MAYBE ADD CUSTOM INPUT FOR CREATING PLOTS ##############
#################################################################

if __name__ == "__main__":
    app.run(debug=True)