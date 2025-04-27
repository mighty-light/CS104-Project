from flaskwebsite_24b0913 import app
from flask import request, render_template, send_from_directory
from app.config import (
    uploaded_files
)
from app.pathutils import get_csv_path_from_data
from app.uploadutils import upload_file
from app.tableutils import (
    make_structured_csv,
    prepare_filtered_csv_file,
    display_table,
    download_filtered_table,
)
from app.plotutils import create_plots
from app.utils import (
    get_file_data,
    find_start_date,
    find_end_date,
)


@app.route("/")
def main():
    return render_template("main.html", title="Welcome to Log Analysis Platform")


@app.route("/upload", methods=[ 'GET', 'POST' ])
def upload():
    if request.method == 'POST':
        upload_file()
    return render_template("upload.html", title="Upload Files", file_info=uploaded_files)


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

### NOTE: Much of the hard coding (if else) can be removed if we use the
### mktime() function of awk that will calculate the time from epoch.
### It will also work with weird date-time choices, e.g., daylight savings.

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