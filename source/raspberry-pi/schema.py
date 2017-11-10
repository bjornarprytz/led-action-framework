import sqlite3 as lite

db_folder = 'db/'

class db:
    class schema:
        def __init__(self):
            experiment = '''
                CREATE TABLE IF NOT EXISTS experiments
                (id INTEGER PRIMARY KEY NOT NULL,
                start DATETIME,
                duration DATETIME,
                normalization INTEGER
                notes VARCHAR(64))
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

            self.tables_init = [experiment, readings]

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
            (timestamp, temperature, humidity, co2),
            (timestamp, temperature, humidity, co2),
            ...
            (timestamp, temperature, humidity, co2), #This trailing comma is important!
            ]
        '''
        db = lite.connect(self.path)
        c = db.cursor()

        c.execute('INSERT INTO readings VALUES (?,?,?,?,?)', records)

        db.commit()
        db.close()

    def new_experiment(self, start_time, duration, normalization):
        db = lite.connect(self.path)
        c = db.cursor()

        values = (start_time, duration, normalization,)

        c.execute('INSERT INTO experiments(start, duration, normalization) VALUES(?,?,?)', values)

        experiment_id = c.lastrowid

        db.commit()
        db.close()

        return experiment_id

if __name__ == "__main__":
    s = db("new")
    s.init_db()
    print s.new_experiment("123", "141", "124")
