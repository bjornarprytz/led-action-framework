import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import json
import datetime


def make_plot(param, data):
    #Current time

    times = []
    plots = []

    for entry in data:
        t = entry['timestamp']
        date = datetime.datetime.strptime(t, "%H:%M")
        times.append(date)
        plots.append(entry[param])

    print times

    print plots

    # Look back 120 minutes. TODO: Adjust this to fit actual interval times
    fig, ax = plt.subplots()

    # Title the plot
    plt.title(param + "  " + data[-1]['timestamp'])
    ax.plot(times, plots)

    # Format the x-axis to Hours : Minutes
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.gcf().autofmt_xdate()

    # Save the result as a .SVG
    folder = 'html/'
    plt.savefig(folder+param+'.svg')


if __name__ == "__main__":
    fn = datetime.datetime.now().strftime("%d%m%y.json")
    folder = "JSON/"
    path = folder + fn
    with open(path) as data_file:
        json = json.load(data_file)
    if len(json) > 0:
        recent_data = json
        make_plot('temperature', recent_data)
        make_plot('humidity', recent_data)
        make_plot('co2', recent_data)
    else:
        print "lacking data"
