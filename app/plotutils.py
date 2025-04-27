import os
import numpy as np
import matplotlib.pyplot as plt
from app.config import (
    IMAGE_FOLDER
)
from app.pathutils import (
    get_image_name,
    get_image_path
)
from app.utils import most_common

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
        year = str(1970) # Year is not provided in logs so we use the Unix epoch

    return np.datetime64(year + '-' +  month + '-' +  day + 'T' + hrs + ':' + mnt + ':' + sec)