import datetime
import RPicontrol
import time

if __name__ == "__main__":
    update_interval = 40 # seconds
    warmup_interval = 10 # minutes
    now = last_update = last_warmup = datetime.datetime.now()

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
            handler.update(auto_reset=True)
            handler.log(experiment_id)
            last_update = datetime.datetime.now()

        # if now - last_warmup >= datetime.timedelta(minutes=warmup_interval):
        #     print "Initiating warm-up (reset):", now
        #     handler.reset_sensors()
        #     last_warmup = datetime.datetime.now()

        time.sleep(1) # not to take up too much CPU time
