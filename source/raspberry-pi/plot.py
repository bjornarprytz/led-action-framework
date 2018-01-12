#!/usr/bin/python

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import json
import datetime
import os.path
import database
from pprint import pprint

db_name = "plantdb"
dst_folder = "static/assets/"
days_postfix = "_days.json"
hour_postfix = "_H.json"
experiment_postfix = "_exp.json"
recent_fn = "recent.json" # labels for the recent hours
week_fn = "weeks.json" # labels for the past days (a week)
intervals_fn = "intervals.json" # labels for the intervals in an experiment
params = ['temp', 'hum', 'co2']
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
            '%H' : [(0, temp, hum, co2) (1, temp, hum, co2), ... (59, temp, hum, co2)]
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

            json['temp'][h]['values'][m] = temp
            json['hum'][h]['values'][m] = hum
            json['co2'][h]['values'][m] = co2

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

            json['temp'][d]['values'][h] = temp
            json['hum'][d]['values'][h] = hum
            json['co2'][d]['values'][h] = co2

    # Write the JSON to files: 'static/assets/temp_days.json' etc.
    for param in params:
        days_path = dst_folder+param+days_postfix
        write_json(days_path, json[param])

    week_path = dst_folder+week_fn
    write_json(week_path, week)

def plot_experiment(title, filename):
    '''
        Plot the CO2 levels over an interval
    '''

    db = database.db(db_name)

    readings_by_interval = db.get_readings_from_experiment_by_interval(title)
    # print readings_by_interval

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    co2_fig = plt.figure()
    co2_ax = co2_fig.add_subplot(111)

    i = 0
    for interval in readings_by_interval:
        if len(interval) < 1:
            continue
        t = 0
        temp = []
        hum = []
        co2 = []
        time = []
        for reading in interval:
            time.append(t)
            co2.append(reading[3])
            t+=1

        plt.plot(time, co2, '.-', color=colors[i%len(colors)])
        i += 1

    co2_ax.axis([0, t-1, 300, 1000])
    plt.ylabel('CO2 ppm')
    plt.xlabel('Time (minutes)')
    plt.savefig(filename)


    # Title - Date

    # Function for comparing experiments too


def log_experiment(title):
    '''

        DEPRECATED

        Make JSON for each inteval in an experiment
    '''

    print "DEPRECATED FUNCTION: log_experiment()"

    return

    db = database.db(db_name)

    readings_by_interval = db.get_readings_from_experiment_by_interval(title)


    num_intervals = len(readings_by_interval)
    if num_intervals < 1:
        print 'error finding experiment: ',title, num_intervals,' intervals'
        return

    # Create the JSON file for the labels (interval id)
    interval_labels = range(num_intervals)
    interval_labels_path = dst_folder+intervals_fn
    write_json(interval_labels_path, interval_labels)

    readings_per_interval = len(readings_by_interval[0])

    json = {} # This will catalogue readings by minutes and interval and parameter

    for param in params:
        json[param] = []
        for i in range(num_intervals):
            json[param].append({'values': [0] * readings_per_interval})

    for i in range(num_intervals):              # For each interval
        t=0                                     # Keep count on the time
        for reading in readings_by_interval[i]: # For each reading
            if t >= readings_per_interval:
                break
            temp = reading[1]
            hum = reading[2]
            co2 = reading[3]

            json['temp'][i]['values'][t] = temp
            json['hum'][i]['values'][t] = hum
            json['co2'][i]['values'][t] = co2

            t+=1

    for param in params:
        experiment_path = dst_folder+title+param+experiment_postfix
        write_json(experiment_path, json[param])

    '''
        JSON:
        {
            'param':[ ***interval***
                        {'values' : [0,0,0,....,0]}, ***t=0***
                        {'values' : [0,0,0,....,0]}, ***t=1***
                        ...
                        {'values' : [0,0,0,....,0]}  ***t=rpi-1***
                    ]
                    ...
                    [
                        'values'...
                    ]
            ...
        }
    '''

if __name__ == "__main__":
    # make_plot()
    #now = datetime.datetime.now()
    #log_hours(now)
    #log_days(now)
    plot_experiment('baseline', 'testfig_co2')
