import os, subprocess
from datetime import datetime

from flask import request
from flaskwebsite_24b0913 import app
from werkzeug.utils import secure_filename
from app.config import (
    SUPPORTED_LOG_FORMATS,
    uploaded_files,
)
from app.pathutils import get_validator_path


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