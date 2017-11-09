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
params = ['temp', 'hum', 'co2']
sensor_fn = "sensor_data.json"

def log_hour(day, hour, param):
    '''
    Return a list of readings of each minute in a given hour.
    '''
    date = day.strftime("%d%m%y")

    sensor_path = src_folder + sensor_fn

    if os.path.isfile(sensor_path):
        sensor_data_file = open(sensor_path, 'r')
        sensor_data_log = json.load(sensor_data_file)

    readings = [0] * 60 # List to store the data
    if date in sensor_data_log.keys():

        total = 0 # Count the magnitude of the readings
        num = 0 # Keep track of the number of readings so that we can aggregate
        m = 0
        prev_m = 0
        for r in sensor_data_log[date]: # For each record
            t = r['time'] # Check the time stamp
            h = datetime.datetime.strptime(t, "%H:%M").hour # We only care about the hour
            m = datetime.datetime.strptime(t, "%H:%M").minute # and the minute
            if h > hour:
                break
            if h == hour:
                if m == prev_m:
                    total += r[param]
                    num += 1
                else:
                    total = r[param]
                    num = 1
                readings[m] = total/num # Update readings each time
                # print "Reading:", readings[m], "hour:", h, "minute:", m
            prev_m = m

    hour_path = dst_folder+param+"_"+str(hour)+hour_fn
    hour_data_file = open(hour_path, 'w')
    hour_data_file.write(json.dumps({'values': readings}))
    hour_data_file.close()

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
    return {'values': readings}

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

    for i in reversed(range(7)):
        day = today - datetime.timedelta(days=i)

        for param in params:
            days[param].append(make_day(sensor_data_log, day, param))

        week.append(day.strftime("%a"))

    for param in params:
        days_path = dst_folder+param+"_"+days_fn
        days_data_file = open(days_path, 'w')
        days_data_log = days[param]
        days_data_file.write(json.dumps(days_data_log))
        days_data_file.close()

    week_path = dst_folder+week_fn
    week_data_file = open(week_path, 'w')

    week_data_log = week

    week_data_file.write(json.dumps(week_data_log))

    week_data_file.close()

if __name__ == "__main__":
    # make_plot()
    log_hour(datetime.datetime.today() - datetime.timedelta(days=1), 12, 'co2')
