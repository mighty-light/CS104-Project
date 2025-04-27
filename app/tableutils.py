
import os, csv, subprocess
from flask import send_file
from flaskwebsite_24b0913 import app
from app.config import (
    STRUCTURED_CSV_FOLDER,
    PARSER_FOLDER
)
from app.pathutils import (
    get_csv_path_from_data,
    get_filter_script,
)

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