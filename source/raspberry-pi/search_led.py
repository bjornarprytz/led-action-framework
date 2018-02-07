from RPicontrol import *
import plot

def __parse_args():
    '''
        private function for running this script
    '''
    if len(sys.argv) < 2:
        print "Usage: python", sys.argv[0], "num_intervals red white blue ... red white blue"
        exit()

    num_intervals = int(sys.argv[1])

    if len(sys.argv[2:]) % 3 != 0:
        print "Bad number of arguments. settings should be input in threes: red white blue"
        exit()


    arguments = sys.argv[2:]

    num_settings = len(arguments) / 3

    settings = []

    for i in range(num_settings):
        base = i * 3
        red = int(arguments[base])
        white = int(arguments[base+1])
        blue = int(arguments[base+2])

        settings.append([red, white, blue])


    return num_intervals, settings

if __name__ == "__main__":
    num_intervals, settings = __parse_args()

    normalization_time = 420
    interval_length = 480
    description = "Settings:"+str(settings)

    ETA = ((normalization_time + interval_length) * num_intervals * len(settings)) / 60

    print 'Search start: ',datetime.datetime.now()
    print 'Running searches: this should take about', ETA, 'minutes'
    print 'ETA: ', (datetime.datetime.now() + datetime.timedelta(minutes=ETA))
    print 'Settings: ', settings

    handler = PlantEnvironmentControl()

    today = datetime.datetime.today()

    title = 'search_'+today.strftime("%d%m%H")
    print 'title:',title

    # NOTE: normalization_time is put into description for data collection later.
    handler.run_search(title, description, interval_length, num_intervals, normalization_time, settings)

    print 'experiment done'
