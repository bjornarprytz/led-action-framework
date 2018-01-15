import datetime
import plot
import time

if __name__ == "__main__":
    update_interval = 1 # minutes

    now = last_update = datetime.datetime.now()

    while True:
        if now - last_update >= datetime.timedelta(minutes=update_interval):
            print "Updating JSON: ", now
            plot.log_hours(now)
            plot.log_days(now)
            last_update = datetime.datetime.now()

            time.sleep(1) # not to take up too much CPU time
