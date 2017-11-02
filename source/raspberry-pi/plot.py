import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import json
import datetime
import os.path

src_folder = "html/JSON/"
dst_folder = "static/assets/"
week_fn = "weeks.json"
days_fn = "days.json"
params = ['temp', 'hum', 'co2']
sensor_fn = "sensor_data.json"

def make_day(sensor_data_log, day, param):
    date = day.strftime("%d%m%y")

    if date in sensor_data_log.keys():
        counter = 0
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

def make_week():
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

def make_plot():
    make_week()



if __name__ == "__main__":
    make_plot()
