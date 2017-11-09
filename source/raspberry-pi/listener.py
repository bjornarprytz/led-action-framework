import datetime
import RPiserial
import plot

if __name__ == "__main__":
    update_interval = 10 # seconds
    log_interval = 60 # seconds
    plot_interval = 2 # minutes
    last_plot = last_log = last_update = datetime.datetime.now()

    handler = RPiserial.PlantEnvironmentControl()
    while True:
        now = datetime.datetime.now()
        if now - last_update >= datetime.timedelta(seconds=update_interval):
            print "updating: ", now
            handler.update()
            last_update = datetime.datetime.now()

        if now - last_log >= datetime.timedelta(seconds=log_interval):
            print "logging: ", now
            handler.log()
            last_log = datetime.datetime.now()

        if now - last_plot >= datetime.timedelta(minutes=plot_interval):
            print "plotting: ", now
            plot.log_week()
            last_plot = datetime.datetime.now()
