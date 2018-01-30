from RPicontrol import *
import plot

def __parse_args():
    '''
        private function for running this script
    '''
    if len(sys.argv) < 4:
        print "Usage: python", sys.argv[0], "interval_seconds normalization_seconds, num_intervals[, red][, white][, blue]"
        exit()

    interval_length = int(sys.argv[1])
    normalization_time = int(sys.argv[2])
    num_intervals = int(sys.argv[3])

    setting = {}

    if len(sys.argv) == 7:
        red = int(sys.argv[4])
        white = int(sys.argv[5])
        blue = int(sys.argv[6])
        setting={'r':red, 'w':white, 'b':blue}
    else:
        setting={'r':0xFF, 'w':0xFF, 'b':0xFF}


    return interval_length, normalization_time, num_intervals, setting

if __name__ == "__main__":
    interval_length, normalization_time, num_intervals, setting = __parse_args()

    ETA = ((normalization_time + interval_length)*num_intervals) / 60

    print 'Batch start: ',datetime.datetime.now()
    print 'Running batches: this should take about', ETA, 'minutes'
    print 'ETA: ', (datetime.datetime.now() + datetime.timedelta(minutes=ETA))
    print 'Setting: ', setting

    handler = PlantEnvironmentControl()

    today = datetime.datetime.today()

    title = 'baseline_'+today.strftime("%d%m%H")
    print 'title:',title

    # NOTE: normalization_time is put into description for data collection later.
    handler.run_experiment(title, normalization_time, interval_length, num_intervals, normalization_time, seed_setting=setting)

    plot.plot_experiment(title, title)
    print 'experiment done'
