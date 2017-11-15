import datetime
import RPiserial
import plot
import time

if __name__ == "__main__":
    update_interval = 10 # seconds
    plot_interval = 1 # minutes
    now = last_plot = last_log = last_update = datetime.datetime.now()

    handler = RPiserial.PlantEnvironmentControl()
    experiment_id = handler.db.new_experiment("test experiment", now, '', '')

    while True:
        now = datetime.datetime.now()
        if now - last_update >= datetime.timedelta(seconds=update_interval):
            print "updating(and logging): ", now
            handler.update()
            handler.log(experiment_id)
            last_update = datetime.datetime.now()


        if now - last_plot >= datetime.timedelta(minutes=plot_interval):
            print "plotting: ", now
            plot.log_hours(experiment_id, now)
            plot.log_days(experiment_id, now)
            last_plot = datetime.datetime.now()

        time.sleep(1) # not to take up too much CPU
