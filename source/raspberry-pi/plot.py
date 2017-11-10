import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import json
import datetime
import os.path

src_folder = "JSON/"
dst_folder = "static/assets/"
week_fn = "weeks.json"
days_fn = "days.json"
hour_fn = "H.json"
recent_fn = "recent.json"
params = ['temp', 'hum', 'co2']
sensor_fn = "sensor_data.json"

def log_hours(day):
    '''
    Return minute by minute readings from the last (12) hours
    '''
    date = day.strftime("%d%m%y")
    hours = day.hour+1
    readings = {}
    for param in params:
        readings[param] = [{'values': [0] * 60}] * hours # List to store the data

    recent = range(hours) # Make a list of the hours we are logging

    sensor_path = src_folder + sensor_fn

    if os.path.isfile(sensor_path):
        sensor_data_file = open(sensor_path, 'r')
        sensor_data_log = json.load(sensor_data_file)


    hcount=0

    if date in sensor_data_log.keys():
        for hour in recent:
            total = 0 # Note the magnitude of the readings
            num = 0 # Keep track of the number of readings so that we can aggregate
            m = 0 # Count the minutes
            for r in sensor_data_log[date]: # For each record
                t = r['time'] # Check the time stamp
                h = datetime.datetime.strptime(t, "%H:%M").hour # Check if it's the right hour
                if h == hour:
                    m = datetime.datetime.strptime(t, "%H:%M").minute # and the minute
                    for param in params:
                        # print "found", h
                        readings[param][h]['values'][m] = r[param] # Update readings each time
                        # print "Reading:", readings[m], "hour:", h, "minute:", m
    print len(sensor_data_log[date])

    for param in params:
        hour_path = dst_folder+param+"_"+hour_fn
        write_json(hour_path, readings[param])

    sensor_data_file.close()

    recent_path = dst_folder+recent_fn
    write_json(recent_path, recent)



def write_json(path, to_write, perm='w'):
    fi = open(path, perm)
    fi.write(json.dumps(to_write))
    fi.close()

def log_day(sensor_data_log, day, param):
    date = day.strftime("%d%m%y")

    if date in sensor_data_log.keys():
        readings = []
        for hour in range(24):
            total = 0
            num = 0
            for r in sensor_data_log[date]:
                t = r['time']
                h = datetime.datetime.strptime(t, "%H:%M").hour
                if h > hour:
                    break
                if h == hour:
                    total += r[param]
                    num += 1
            if num > 0:
                readings.append(total/num)
            else:
                readings.append(0)
    else:
        readings = [0]*24
    return readings

def log_week():
    today = datetime.datetime.today()

    week = []
    days = {}
    for param in params:
        days[param] = []

    sensor_path = src_folder + sensor_fn

    if os.path.isfile(sensor_path):
        sensor_data_file = open(sensor_path, 'r')
        sensor_data_log = json.load(sensor_data_file)

    for i in reversed(range(7)): # Go backwards from today
        day = today - datetime.timedelta(days=i)

        # Collect the sensor data from this day
        for param in params:
            days[param].append(make_day(sensor_data_log, day, param))

        # Add to the week
        week.append(day.strftime("%a"))

    sensor_data_file.close()

    # Write the data to file
    for param in params:
        days_path = dst_folder+param+"_"+days_fn
        days_data_log = days[param]
        write_json(days_path, days_data_log)

    # Write the last 7 days to file
    week_path = dst_folder+week_fn
    write_json(week_path, week)



if __name__ == "__main__":
    # make_plot()
    log_hours(datetime.datetime.now() - datetime.timedelta(days=2))
