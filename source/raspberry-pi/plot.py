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
week_fn = "weeks.json"
days_postfix = "_days.json"
hour_postfix = "_H.json"
recent_fn = "recent.json"
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
            h = int(r[0][-2:])   # Hour
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

if __name__ == "__main__":
    # make_plot()
    now = datetime.datetime.now()
    log_hours(now)
    log_days(now)
