from flask import request
from app.config import (
    uploaded_files,
    FROM_TIME_LADDER,
    TO_TIME_LADDER,
)


def get_file_data(html_name):
    return [file_data for file_data in uploaded_files if file_data['name'] == request.form.get(html_name)][0]

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

def most_common(dictionary, k):
    return sorted(dictionary.items(), key=lambda x: x[1], reverse=True)[:k]
