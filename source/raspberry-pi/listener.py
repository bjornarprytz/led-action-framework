import datetime
import RPicontrol
import plot
import time

if __name__ == "__main__":
    update_interval = 10 # seconds
    now = last_update = datetime.datetime.now()

    interval_length = 300 # seconds

    handler = RPicontrol.PlantEnvironmentControl()
    experiment_id = handler.db.new_experiment("test experiment", now, interval_length, '')
    settings = [
    128,
    135,
    69,
    experiment_id,
    ]
    interval_id = handler.db.new_interval(settings)

    while True:
        now = datetime.datetime.now()
        if now - last_update >= datetime.timedelta(seconds=update_interval):
            print "updating(and logging): ", now
            handler.update()
            handler.log(experiment_id)
            last_update = datetime.datetime.now()

        time.sleep(1) # not to take up too much CPU time
