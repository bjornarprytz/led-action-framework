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
                duration DATETIME,
                normalization INTEGER
                )
            '''

            readings = '''
                CREATE TABLE IF NOT EXISTS readings
                (id INTEGER PRIMARY KEY,
                collect_time DATETIME,
                temperature REAL,
                humidity REAL,
                co2 REAL,
                experiment_key INT NOT NULL,
                FOREIGN KEY(experiment_key) REFERENCES experiments(id))
            '''

            self.tables_init = [experiments, readings]

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

    def insert_readings(self, records):
        '''
            records should be a list of tuples, on the form:
            [
            (collect_time, temperature, humidity, co2, experiment_key),
            (collect_time, temperature, humidity, co2, experiment_key),
            ...
            (collect_time, temperature, humidity, co2, experiment_key)
            ]
        '''
        db = lite.connect(self.path)
        c = db.cursor()

        c.execute('INSERT INTO readings(collect_time, temperature, humidity, co2, experiment_key) VALUES (?,?,?,?,?)', records)

        db.commit()
        db.close()

    def insert_reading(self, record):
        insert_readings([record])

    def new_experiment(self, title, start_time, duration, normalization, description=''):
        db = lite.connect(self.path)
        c = db.cursor()

        values = (title, description, start_time, duration, normalization)

        try:
            c.execute('INSERT INTO experiments(title, description, start, duration, normalization) VALUES(?,?,?,?,?)', values)
            experiment_key = c.lastrowid
        except lite.IntegrityError as e:
            print('sqlite error: ', e.args[0])
            experiment_key = self.experiment_exists(title)


        db.commit()
        db.close()

        return experiment_key

    def get_readings(self, SQL, values):
        '''
            General helper function that queries the DB
        '''
        db = lite.connect(self.path)
        c = db.cursor()

        c.execute(SQL, values)

        readings = c.fetchall()
        db.close()

        return readings

    def get_readings_hour(self, experiment_key, hour):
        '''
            returns an average of temperature, humidity and co2,
            over the given _hour_ grouped by minutes
        '''
        values = (experiment_key,hour,)

        SQL =   '''
                SELECT strftime('%H%M', collect_time), AVG(temperature), AVG(humidity), AVG(co2)
                FROM readings
                WHERE experiment_key=? AND strftime('%Y-%m-%dT%H', collect_time)=?
                GROUP BY strftime('%Y-%m-%dT%H:%M:00', collect_time)
                '''
        return self.get_readings(SQL, values)

    def get_readings_day(self, experiment_key, day):
        '''
            returns an average of temperature, humidity and co2,
            over the given _day_, grouped by hours
        '''
        values = (experiment_key,day,)

        SQL =   '''
                SELECT strftime('%Y-%m-%dT%H', collect_time), AVG(temperature), AVG(humidity), AVG(co2)
                FROM readings
                WHERE experiment_key=? AND strftime('%Y-%m-%d', collect_time)=?
                GROUP BY strftime('%Y-%m-%dT%H:00:00', collect_time)
                '''

        return self.get_readings(SQL, values)

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

if __name__ == "__main__":
    s = db("debug")
    s.init_db()
    key = s.new_experiment("old silly experiment", "123", "141", "124")

    date = dt.datetime.now()

    s.insert_readings((date, 22.3, 465.23, 124.12, key))

    print s.get_readings(3, where='temperature BETWEEN 20.5 AND 25.0')

    print s.experiment_exists("old silly experiment")
    print s.experiment_exists("non-existent experiment")
