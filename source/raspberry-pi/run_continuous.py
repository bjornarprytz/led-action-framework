from RPicontrol import *
import plot

def __parse_args():
    '''
        private function for running this script
    '''
    if len(sys.argv) < 3:
        print "Usage: python", sys.argv[0], "interval_seconds num_intervals"
        exit()

    interval_length = int(sys.argv[1])
    num_intervals = int(sys.argv[2])


    return interval_length, num_intervals

if __name__ == "__main__":
    interval_length, num_intervals = __parse_args()

    ETA = ((interval_length)*num_intervals*2) / 60

    print 'Start time: ',datetime.datetime.now()
    print 'Running batches: this should take about', ETA, 'minutes'
    print 'ETA: ', (datetime.datetime.now() + datetime.timedelta(minutes=ETA))

    handler = PlantEnvironmentControl()

    today = datetime.datetime.today()

    title = 'continuous_'+today.strftime("%d%m%H")
    print 'title:',title

    # NOTE: normalization_time is put into description for data collection later.
    handler.run_continuous_intervals(title, interval_length, num_intervals)

    plot.plot_experiment(title, title)
    print 'experiment done'
