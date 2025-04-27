import os
from app.config import (
        IMAGE_FOLDER,
        STRUCTURED_CSV_FOLDER,
        FILTER_SCRIPT_FOLDER,
        VALIDATOR_FOLDER,
    )

def get_image_path(filepath, extension):
    return os.path.join(IMAGE_FOLDER, f"plot_{os.path.basename(filepath)}.{extension}")

def get_image_name(filepath, extension):
    return f"plot_{os.path.basename(filepath)}.{extension}"

def get_csv_path_from_data(file_data, filtered=False):
    if not filtered:
        return os.path.join(STRUCTURED_CSV_FOLDER, f"{file_data['name']}_structured.csv")
    return os.path.join(STRUCTURED_CSV_FOLDER, f"filtered_{file_data['name']}_structured.csv")

def get_filter_script(file_data):
    return os.path.join(FILTER_SCRIPT_FOLDER, f"{file_data['type']}_filter.sh")

def get_validator_path(kind):
    return os.path.join(VALIDATOR_FOLDER, f"{kind}_validator.sh")

