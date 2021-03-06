#!/usr/bin/python

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import json
import datetime
import os.path
import database
import numpy as np
import sys
from pprint import pprint

db_name = "plantdb"
dst_folder = "static/assets/"
fig_folder = "figures/"
days_postfix = "_days.json"
hour_postfix = "_H.json"
experiment_postfix = "_exp.json"
recent_fn = "recent.json" # labels for the recent hours
week_fn = "weeks.json" # labels for the past days (a week)
intervals_fn = "intervals.json" # labels for the intervals in an experiment
params = ['temp', 'hum', 'co2', 'co2_ext']
date_format = '%Y-%m-%d %H:%M:%S'

def log_hours(start, num_hours=6):
    '''
    Return minute by minute readings from the last (6) hours (from now)
    '''

    if (num_hours < 1):
        print "must have at least 1 hour to log"

    db = database.db(db_name)

    readings = []
    recent = []
    for h in reversed(range(num_hours)):
        hour = (start - datetime.timedelta(hours=h)).strftime('%Y-%m-%dT%H')
        recent.append(hour[-2:]) # The contents of this list will be used for labels in presentation
        # Query DB
        readings.append(db.get_readings_hour(hour)) # Gets the aggregate of readings each minute that hour
    '''
        readings= {
            '%H' : [(0, temp, hum, co2, co2_ext) (1, temp, hum, co2, co2_ext), ... (59, temp, hum, co2, co2_ext)]
            ... *num_hours
        }
    '''

    json = {} # This will catalogue the readings by minutes, hours and parameter
    for param in params:
        json[param] = []
        for h in range(num_hours):
            json[param].append({'values': [0] * 60}) # List to store the data

    for h in range(num_hours): # For each hour..
        for r in readings[h]:  # One reading per minute
            m = int(r[0][-2:])   # Minute
            temp = r[1]     # Temperature
            hum = r[2]      # Humidity
            co2 = r[3]      # Carbon-Dioxide
            co2_ext = r[4]  # External CO2

            json['temp'][h]['values'][m] = temp
            json['hum'][h]['values'][m] = hum
            json['co2'][h]['values'][m] = co2
            json['co2_ext'][h]['values'][m] = co2_ext

    '''
        JSON:
        {
            'param':[ ***hours***
                        {'values' : [0,0,0,....,0]}, ***minutes***
                        {'values' : [0,0,0,....,0]},
                        ...
                        {'values' : [0,0,0,....,0]}
                    ]
                    ...
                    [
                        'values'...
                    ]
            ...
        }
    '''

    # Write the JSON to files: 'static/assets/temp_H.json' etc.
    for param in params:
        hour_path = dst_folder+param+hour_postfix
        write_json(hour_path, json[param])

    recent_path = dst_folder+recent_fn

    write_json(recent_path, recent)

def write_json(path, to_write, perm='w'):
    '''
        Writes json to a file at path. Default mode is to overwrite any existing file.
    '''
    fi = open(path, perm)
    fi.write(json.dumps(to_write))
    fi.close()

def log_days(start, num_days=7):
    if (num_days < 1):
        print "must have at least 1 day to log"

    db = database.db(db_name)

    readings = []
    week = []
    for d in reversed(range(num_days)):
        day = start - datetime.timedelta(days=d)
        day_fmt = day.strftime('%Y-%m-%d')
        week_day = day.strftime('%a')
        week.append(week_day) # The contents of this list will be used for labels in presentation
        # Query DB
        readings.append(db.get_readings_day(day_fmt)) # Gets the an aggregate of readings each hour of the day

    json = {} # This will catalogue the readings by hours days and parameter
    for param in params:
        json[param] = []
        for d in range(num_days):
            json[param].append({'values': [0] * 24})

    for d in range(num_days):   # For each day
        for r in readings[d]:   # For each hour
            h = int(r[0][-2:])  # Hour
            temp = r[1]         # Temperature
            hum = r[2]          # Humidity
            co2 = r[3]          # Carbon-Dioxide
            co2_ext = r[4]      # External CO2

            json['temp'][d]['values'][h] = temp
            json['hum'][d]['values'][h] = hum
            json['co2'][d]['values'][h] = co2
            json['co2_ext'][d]['values'][h] = co2_ext

    # Write the JSON to files: 'Startic/assets/temp_days.json' etc.
    for param in params:
        days_path = dst_folder+param+days_postfix
        write_json(days_path, json[param])

    week_path = dst_folder+week_fn
    write_json(week_path, week)

def get_colors(num_hues):

    base_value = 0x40
    max_value = 0xFF


    if num_hues > max_value - base_value:
        print 'asking for too many hues', num_hues
        num_hues = max_value - base_value
    elif num_hues < 1:
        num_hues = 1


    red_range = range(num_hues)
    green_range = range(num_hues)
    blue_range = range(num_hues)

    step = (max_value - base_value) / num_hues


    for v in range(num_hues):
        value = base_value + v*step

        red = value << 16
        green = value << 8
        blue = value

        red_range[v] = '#'+str(hex(red))[2:]
        green_range[v] = '#00'+str(hex(green))[2:]
        blue_range[v] = '#0000'+str(hex(blue))[2:]

    colors = {'r' : red_range, 'g' : green_range, 'b' : blue_range}

    return colors

def plot_experiment(title, filename):
    '''
        Plot the various measurements of intervals in the same experiment against
        each other and save the figure in a folder
    '''

    db = database.db(db_name)

    readings_by_interval = db.get_readings_from_experiment_by_interval(title)
    # print readings_by_interval

    co2_by_interval = []
    hum_by_interval = []
    temp_by_interval = []
    co2_ext_by_interval = []
    for interval in readings_by_interval:
        if len(interval) < 1:
            continue
        temp = []
        hum = []
        co2 = []
        co2_ext = []
        for reading in interval:
            print reading[0]
            temp.append(reading[1])
            hum.append(reading[2])
            co2.append(reading[3])  # Rate of CO2 consumption
            co2_ext.append(reading[4])

        co2_by_interval.append(co2)
        hum_by_interval.append(hum)
        temp_by_interval.append(temp)
        co2_ext_by_interval.append(co2_ext)

    time = range(len(interval))
    colors = get_colors(len(readings_by_interval))

    try:
        description = db.get_experiment_description(title)[0][0]
        normalization_time = float(description) / 60.0 # Minutes
    except ValueError:
        normalization_time=0
        print 'could not extract normalization_time from database'

    co2_axis = plt.subplot(211)
    co2_axis.axis([time[0], time[-1], 300, 750])
    plt.title(str(len(readings_by_interval))+' intervals with identical system settings')
    plt.setp(co2_axis.get_xticklabels(), visible=False) # Hide the x-axis values
    plt.ylabel('CO2 delta')
    plt.axvline(normalization_time)

    i=0
    for co2_series in co2_by_interval:
        plt.plot(co2_series, '.-', color=colors['r'][i])
        i+=1

    i = 0
    for co2_ext_series in co2_ext_by_interval:
        plt.plot(co2_ext_series,  color=colors['g'][i])
        i+=1

    hum_axis = plt.subplot(413, sharex=co2_axis)
    hum_axis.axis([time[0], time[-1], 0, 100])
    plt.setp(hum_axis.get_xticklabels(), visible=False)
    plt.ylabel('Rel humidity')
    plt.axvline(normalization_time)

    i=0
    for hum_series in hum_by_interval:
        plt.plot(hum_series, '.-', color=colors['b'][i])
        i+=1

    temp_axis = plt.subplot(414, sharex=co2_axis)
    temp_axis.axis([time[0], time[-1], 18, 32])
    plt.ylabel('Temperature (C)')
    plt.xlabel('Time (minutes)')
    plt.axvline(normalization_time)

    i=0
    for temp_series in temp_by_interval:
        plt.plot(temp_series, '.-', color=colors['g'][i])
        i+=1

    plt.savefig(fig_folder+filename)




def get_time_stamp(reading):
    return int(reading[0][-5:-3])*60 + int(reading[0][-2:])

def plot_experiment_mean(title):
    '''
        Plot internal against external CO2. Collect data from multiple consecutive intervals. Plot the
        mean and the variance (box plot)
    '''
    db = database.db(db_name)

    readings_by_interval = db.get_readings_from_experiment_by_interval(title)

    settings = db.get_experiment_initial_settings(title)[0]

    # All intervals are supposed to be of the same length, but some may lack data, because of anomalous readings
    longest_interval = 0
    for interval in readings_by_interval:
        interval_length = len(interval)
        if interval_length > longest_interval:
            longest_interval = interval_length

    co2_timeline = []
    co2_ext_timeline = []

    for i in range (longest_interval):
        co2_timeline.append([])         # List of lists
        co2_ext_timeline.append([])

    co2_by_interval = []
    co2_ext_by_interval = []
    for interval in readings_by_interval:
        if len(interval) < 1:
            continue
        temp = []
        hum = []
        co2 = []
        co2_ext = []
        base = get_time_stamp(interval[0]) # Time stamp to anchor all the readings to
        for i in range(len(interval)):
            # NOTE: this indexing can go wrong if all intervals are missing readings in the same exact timeslot
            t = get_time_stamp(interval[i]) - base
            # print t
            co2_timeline[t].append(interval[i][3])
            co2_ext_timeline[t].append(interval[i][4])

    y_co2 = []  # hold means of each timeslot
    y_co2_ext = []
    y_co2_error = []
    for timeslot in co2_timeline:
        y_co2.append(np.mean(timeslot))
        y_co2_error.append(np.std(timeslot))
    for timeslot in co2_ext_timeline:
        y_co2_ext.append(np.mean(timeslot))

    fig, ax = plt.subplots()


    # box_data = np.concatenate((y_co2)

    ax.plot(range(longest_interval), y_co2_ext)
    ax.boxplot(co2_timeline, 0, '')  #y_co2, yerr=y_co2_error)

    ax.set_xlim([0, 25])
    ax.set_ylim([300, 800])

    heading = 'r:' + str(settings[0]) + ' w:' + str(settings[1]) + ' b:' + str(settings[2])



    plt.ylabel('CO2 ppm')
    plt.xlabel('Minutes')
    plt.title(heading)

    filename = heading+'_boxplot.pdf'

    fig.savefig(fig_folder+filename)


def plot_hours(start, num_hours=6):
    '''
    Return minute by minute readings from the last (6) hours (from now)
    '''

    if (num_hours < 1):
        print "must have at least 1 hour to log"

    db = database.db(db_name)

    readings = []
    recent = []
    for h in reversed(range(num_hours)):
        hour = (start - datetime.timedelta(hours=h)).strftime('%Y-%m-%dT%H')
        recent.append(hour[-2:]) # The contents of this list will be used for labels in presentation
        # Query DB
        readings.append(db.get_readings_hour_no_co2_ext(hour)) # Gets the aggregate of readings each minute that hour
    '''
        readings= {
            '%H' : [(0, temp, hum, co2, co2_ext) (1, temp, hum, co2, co2_ext), ... (59, temp, hum, co2, co2_ext)]
            ... *num_hours
        }
    '''

    json = {} # This will catalogue the readings by minutes, hours and parameter
    for param in params:
        json[param] = []
        for h in range(num_hours):
            json[param].append([0] * 60) # List to store the data

    for h in range(num_hours): # For each hour..
        for r in readings[h]:  # One reading per minute
            m = int(r[0][-2:])   # Minute
            temp = r[1]     # Temperature
            hum = r[2]      # Humidity
            co2 = r[3]      # Carbon-Dioxide
            # co2_ext = r[4]  # External CO2

            json['temp'][h][m] = temp
            json['hum'][h][m] = hum
            json['co2'][h][m] = co2
            # json['co2_ext'][h][m] = co2_ext

    y = []  # hold means of each timeslot
    # y_co2_ext = []
    y_error = []
    for timeslot in json['hum']:
        y.append(np.mean(timeslot))
        y_error.append(np.std(timeslot))
    # for timeslot in json['co2_ext']:
        # y_co2_ext.append(np.mean(timeslot))

    fig, ax = plt.subplots()

    # ax.plot(range(num_hours), y_co2_ext)
    ax.errorbar(range(num_hours), y, yerr=y_error)

    ax.set_xlim([0, num_hours-1])
    ax.set_ylim([15, 25])

    plt.ylabel('Relative Humidity')
    plt.xlabel('Hours')

    filename = 'a_day_hum'+'_std_error.pdf'

    fig.savefig(fig_folder+filename)

    # Title - Date

    # Function for comparing experiments too
# def log_experiment(title):
#     '''
#
#         DEPRECATED
#
#         Make JSON for each inteval in an experiment
#     '''
#
#     print "DEPRECATED FUNCTION: log_experiment()"
#
#     return
#
#     db = database.db(db_name)
#
#     readings_by_interval = db.get_readings_from_experiment_by_interval(title)
#
#
#     num_intervals = len(readings_by_interval)
#     if num_intervals < 1:
#         print 'error finding experiment: ',title, num_intervals,' intervals'
#         return
#
#     # Create the JSON file for the labels (interval id)
#     interval_labels = range(num_intervals)
#     interval_labels_path = dst_folder+intervals_fn
#     write_json(interval_labels_path, interval_labels)
#
#     readings_per_interval = len(readings_by_interval[0])
#
#     json = {} # This will catalogue readings by minutes and interval and parameter
#
#     for param in params:
#         json[param] = []
#         for i in range(num_intervals):
#             json[param].append({'values': [0] * readings_per_interval})
#
#     for i in range(num_intervals):              # For each interval
#         t=0                                     # Keep count on the time
#         for reading in readings_by_interval[i]: # For each reading
#             if t >= readings_per_interval:
#                 break
#             temp = reading[1]
#             hum = reading[2]
#             co2 = reading[3]
#
#             json['temp'][i]['values'][t] = temp
#             json['hum'][i]['values'][t] = hum
#             json['co2'][i]['values'][t] = co2
#
#             t+=1
#
#     for param in params:
#         experiment_path = dst_folder+title+param+experiment_postfix
#         write_json(experiment_path, json[param])
#
#     '''
#         JSON:
#         {
#             'param':[ ***interval***
#                         {'values' : [0,0,0,....,0]}, ***t=0***
#                         {'values' : [0,0,0,....,0]}, ***t=1***
#                         ...
#                         {'values' : [0,0,0,....,0]}  ***t=rpi-1***
#                     ]
#                     ...
#                     [
#                         'values'...
#                     ]
#             ...
#         }
#     '''

# def plot_search_mean(title, red, white, blue):
#     db = database.db(db_name)
#
#     intervals = db.get_readings_from_experiment_by_setting_and_interval(title, red, white, blue)
#
#     relevant = []
#     for interval in intervals:
#         if len(interval) < 11:
#             continue
#         else:
#             relevant.append(interval[:11])
#
#     for interval in relevant:
#         print interval[0][0]
#         # for reading in interval:
#         #     print reading[3]
#         print 'score: ', interval[6][3] - interval[-1][3] # Normalization starts at 7 minutes, reaches bottom ~5 min after that

def score_interval_absolute(interval, norm_time, fitness_time):

    co2_timeline = []

    for reading in interval:
        co2_timeline.append(reading[3])

    return co2_timeline[norm_time] - co2_timeline[fitness_time]

def score_interval_relative_to_ambient_co2(interval, norm_time, fitness_time):
    co2_timeline = []

    ambient_co2 = 400

    for reading in interval:
        co2_timeline.append(reading[3])

    return ambient_co2 - co2_timeline[fitness_time]

def score_interval_relative_to_ext_co2(interval, norm_time, fitness_time):
    co2_timeline = []

    co2_ext_timeline = []

    for reading in interval:
        co2_timeline.append(reading[3])
        co2_ext_timeline.append(reading[4])

    return np.mean(co2_ext_timeline) - co2_timeline[fitness_time]

def estimate_repeatability(titles, scorefunc):
    '''
        comapre experiments with similar settings
    '''
    db = database.db(db_name)


    settings = []
    experiments = []
    for title in titles:
        readings_by_interval = db.get_readings_from_experiment_by_interval(title)

        settings.append(db.get_experiment_initial_settings(title)[0])

        interval_scores = []
        for interval in readings_by_interval:
            interval_scores.append(scorefunc(interval, 8, 17))

        experiments.append(interval_scores)

    print experiments

    fig, ax = plt.subplots()


    # box_data = np.concatenate((y_co2)

    ax.boxplot(experiments, 0, '')  #y_co2, yerr=y_co2_error)

    ax.set_xlim([0, len(titles)+1])
    ax.set_ylim([0, 100])

    heading = 'Comparison of Settings (mean(ExternalCO2) - CO2@16min)'



    plt.ylabel('Fitness')
    plt.xlabel('Setting')
    plt.xticks(range(1, len(titles)+1), ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    plt.title(heading)

    filename = 'Comparison of Settings Relative to externalCO2.pdf'

    fig.savefig(fig_folder+filename)

def __parse_args():
    if len(sys.argv) < 2:
        print "Usage: python", sys.argv[0], "[experiment_title1, experiment_title2, ... experiment_titleN]"
        exit()

    titles = []
    for title in sys.argv[1:]:
        titles.append(title)

    return titles

if __name__ == "__main__":
    # make_plot()
    #now = datetime.datetime.now()
    #log_hours(now)
    #log_days(now)
    # db_name = 'backup/plantdb'
    # plot_hours(datetime.datetime.strptime('2017-11-18 23:00:00', date_format), num_hours=24)

    titles = __parse_args()

    estimate_repeatability(titles, score_interval_relative_to_ext_co2)
