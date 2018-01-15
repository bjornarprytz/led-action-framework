from RPicontrol import *

def __parse_args():
    '''
        private function for running this script
    '''
    if len(sys.argv) < 5:
        print "Usage: python", sys.argv[0], "batch_size interval_seconds normalization_seconds, num_intervals"
        exit()

    batch_size = int(sys.argv[1])
    interval_length = int(sys.argv[2])
    normalization_time = int(sys.argv[3])
    num_intervals = int(sys.argv[4])


    return batch_size, interval_length, normalization_time, num_intervals

if __name__ == "__main__":
    batch_size, interval_length, normalization_time, num_intervals = __parse_args()

    ETA = (((normalization_time + interval_length)*num_intervals)*batch_size) / 60

    print 'running batches: this should take about', ETA, 'minutes'
    print 'ETA: ', (datetime.datetime.now() + datetime.timedelta(minutes=ETA))

    handler = PlantEnvironmentControl()

    today = datetime.datetime.today()

    for b_id in range(batch_size):
        title = 'baseline_'+today.strftime("%d%m")+'_'+str(b_id)

        # NOTE: normalization_time is put into description for data collection later.
        handler.run_experiment(title, normalization_time, interval_length, num_intervals, normalization_time)

        plot.plot_experiment(title, title+'_co2')
        print 'experiment', b_id, 'done'
