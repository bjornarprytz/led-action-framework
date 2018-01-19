import sqlite3 as lite
import datetime as dt

db_folder = 'db/'

class db:
    class schema:
        def __init__(self):
            # NOTE: the limits on VARCHAR() does not seem to be limited in
            # the sqlite3 library, so the caller has to enforce this rule.
            experiments = '''
                CREATE TABLE IF NOT EXISTS experiments
                (id INTEGER PRIMARY KEY NOT NULL,
                title VARCHAR(20) UNIQUE,
                description VARCHAR(64),
                start DATETIME,
                interval_length INTEGER
                )
            '''

            intervals = '''
                CREATE TABLE IF NOT EXISTS intervals
                (id INTEGER PRIMARY KEY NOT NULL,
                red_led INTEGER,
                white_led INTEGER,
                blue_led INTEGER,
                experiment_id INTEGER NOT NULL,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id)
                )
            '''

            readings = '''
                CREATE TABLE IF NOT EXISTS readings
                (id INTEGER PRIMARY KEY,
                collect_time DATETIME,
                temperature REAL,
                humidity REAL,
                co2 REAL,
                co2_ext REAL,
                interval_id INT NOT NULL,
                FOREIGN KEY(interval_id) REFERENCES intervals(id)
                )
            '''

            self.tables_init = [experiments, intervals, readings]

    def __init__(self, name):
        self._schema = self.schema()
        self.path = db_folder + name

    def init_db(self):
        db = lite.connect(self.path)
        c = db.cursor()
        for table in self._schema.tables_init:
            c.execute(table)
        db.commit()
        db.close()

    def new_interval(self, settings):
        db = lite.connect(self.path)
        c = db.cursor()

        c.execute('INSERT INTO intervals(red_led, white_led, blue_led, experiment_id) VALUES (?,?,?,?)', settings)
        interval_id = c.lastrowid

        db.commit()
        db.close()

        return interval_id

    def update_interval(self, interval_id, column_name, value):
        db = lite.connect(self.path)
        c = db.cursor()

        values = (column_name, value, interval_id)

        c.execute('UPDATE intervals SET ?=? WHERE id=?', values)

        db.commit()
        db.close()

    def insert_readings(self, records):
        '''
            records should be a list of tuples, on the form:
            [
            (collect_time, temperature, humidity, co2, co2_ext, interval_id),
            (collect_time, temperature, humidity, co2, co2_ext, interval_id),
            ...
            (collect_time, temperature, humidity, co2, co2_ext, interval_id)
            ]
        '''
        db = lite.connect(self.path)
        c = db.cursor()

        c.execute('INSERT INTO readings(collect_time, temperature, humidity, co2, co2_ext, interval_id) VALUES (?,?,?,?,?,?)', records)

        db.commit()
        db.close()

    def insert_reading(self, record):
        self.insert_readings([record])

    def new_experiment(self, title, start_time, interval_length, description=''):
        '''
            Create a new experiment if it doesn't exist already.
            Returns the id of the experiment.
        '''
        db = lite.connect(self.path)
        c = db.cursor()

        values = (title, description, start_time, interval_length)

        try:
            c.execute('INSERT INTO experiments(title, description, start, interval_length) VALUES(?,?,?,?)', values)
            experiment_id = c.lastrowid
        except lite.IntegrityError as e:
            print('sqlite error: ', e.args[0])
            experiment_id = self.experiment_exists(title)

        db.commit()
        db.close()

        return experiment_id

    def experiment_exists(self, title):
        '''
            Returns False if an experiment with the given title doesn't exist
            Returns the experiment id if at least one such experiment does.
        '''
        db = lite.connect(self.path)
        c = db.cursor()
        values = (title,)

        c.execute('SELECT id FROM experiments WHERE title=?', values)

        readings = c.fetchall()
        db.close()

        if len(readings) > 0:
            return readings[0][0] # The id itself is nested in a tuple and an array
        else:
            return False

    def execute_SQL(self, SQL, values):
        '''
            General helper function that queries the DB
        '''
        db = lite.connect(self.path)
        c = db.cursor()

        c.execute(SQL, values)

        result = c.fetchall()
        db.close()

        return result

    def get_readings_hour(self, hour):
        '''
            returns an average of temperature, humidity and co2,
            over the given _hour_ grouped by minutes
        '''
        values = (hour,)

        SQL =   '''
                SELECT strftime('%H%M', collect_time), AVG(temperature), AVG(humidity), AVG(co2), AVG(co2_ext)
                FROM readings
                WHERE strftime('%Y-%m-%dT%H', collect_time)=?
                GROUP BY strftime('%Y-%m-%dT%H:%M:00', collect_time)
                '''
        return self.execute_SQL(SQL, values)

    def get_readings_day(self, day):
        '''
            returns an average of temperature, humidity and co2,
            over the given _day_, grouped by hours
        '''
        values = (day,)

        SQL =   '''
                SELECT strftime('%Y-%m-%dT%H', collect_time), AVG(temperature), AVG(humidity), AVG(co2), AVG(co2_ext)
                FROM readings
                WHERE strftime('%Y-%m-%d', collect_time)=?
                GROUP BY strftime('%Y-%m-%dT%H:00:00', collect_time)
                '''

        return self.execute_SQL(SQL, values)

    def get_readings_from_experiment_by_interval(self, title):
        '''
            returns all readings from an experiment, averaged and grouped by minute
            listed by interval
        '''

        values = (title,)

        SQL =   '''
                SELECT id
                FROM intervals
                WHERE experiment_id IN
                    (SELECT id
                    FROM experiments
                    WHERE title=?)
                '''

        interval_ids = self.execute_SQL(SQL, values)

        intervals = []

        SQL =   '''
                SELECT strftime('%Y-%m-%dT%H:%M', collect_time), AVG(temperature), AVG(humidity), AVG(co2), AVG(co2_ext)
                FROM readings
                WHERE interval_id=?
                GROUP BY strftime('%Y-%m-%dT%H:%M:00', collect_time)
                '''

        for interval_id in interval_ids:
            values = (interval_id[0],)

            readings = self.execute_SQL(SQL, values)

            intervals.append(readings)

        return intervals

    def get_experiment_description(self, title):

        SQL =   '''
                SELECT description
                FROM experiments
                WHERE title=?
                '''

        values = (title, )

        return self.execute_SQL(SQL, values)

    def print_experiment(self, experiment_title):
        '''
            Prints the parameters and results of an experiment
        '''

        SQL =   '''
                SELECT *
                FROM experiments
                WHERE title=?
                '''
        values = (experiment_title,)

        result = self.execute_SQL(SQL, values)

        if len(result) < 1:
            print 'can\'t find experiment with title', experiment_title

        experiment_metadata = result[0]

        experiment_id = experiment_metadata[0]

        print 'TITLE:           ', experiment_metadata[1]
        print 'Description:     ', experiment_metadata[2]
        print 'start time:      ', experiment_metadata[3]
        print 'interval length: ', experiment_metadata[4]

        SQL =   '''
                SELECT *
                FROM intervals
                WHERE experiment_id IN
                    (SELECT id
                    FROM experiments
                    WHERE title=?
                    )
                '''

        values = (experiment_title,)

        intervals = self.execute_SQL(SQL, values)

        SQL =   '''
                SELECT co2, co2_ext
                FROM readings
                WHERE interval_id=?
                ORDER BY collect_time
                '''

        for interval_metadata in intervals:
            interval_id = interval_metadata[0]

            print '\tInterval id:', interval_id
            print '\t(r, w, b):', (interval_metadata[1], interval_metadata[2], interval_metadata[3])
            values = (interval_id,)
            readings = self.execute_SQL(SQL, values)
            if len(readings) < 2:
                print 'NOT SUFFICIENT READINGS THIS INTERVAL'
            else:
                print '\t\tInitial CO2:', readings[0][0]
                print '\t\t\tDelta:    ', reaidngs[0][1] - readings[0][0]
                print '\t\tEnd CO2:    ', readings[-1][0]
                print '\t\t\tDelta:    ', reaidngs[-1][1] - readings[-1][0]



if __name__ == "__main__":
    s = db("debug")
    s.init_db()
    key = s.new_experiment("old silly experiment", "123", "141", "124")

    date = dt.datetime.now()

    s.insert_readings((date, 22.3, 465.23, 124.12, key))

    print s.get_readings(3, where='temperature BETWEEN 20.5 AND 25.0')

    print s.experiment_exists("old silly experiment")
    print s.experiment_exists("non-existent experiment")
