#!flask/bin/python
from flask import Flask, jsonify, request, make_response, abort, send_from_directory

import datetime
import plot

app = Flask(__name__, static_url_path='/static')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# @app.route('/update')
# def update():
#     print 'updating'
#     plot.log_hours(datetime.datetime.now())
#     plot.log_days(datetime.datetime.now())
#     return app.send_static_file("index.html")

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/last_hour')
def last_hour():
    return app.send_static_file("last_hour.html")

@app.route('/last_week')
def last_week():
    return app.send_static_file("last_week.html")

@app.route('/experiment')
def experiment():
    return app.send_static_file("experiment.html")

@app.route('/intervals')
def intervals():
    return app.send_static_file("assets/intervals.json")

@app.route('/weeks')
def weeks():
    return app.send_static_file("assets/weeks.json")

@app.route('/temperature')
def temperature():
    return app.send_static_file("assets/temp_days.json")

@app.route('/carbon_dioxide')
def carbon_dioxide():
    return app.send_static_file("assets/co2_days.json")

@app.route('/carbon_dioxide_ext')
def carbon_dioxide_ext():
    return app.send_static_file("assets/co2_ext_days.json")

@app.route('/humidity')
def humidity():
    return app.send_static_file("assets/hum_days.json")

@app.route('/temp_hour')
def temp_hour():
    return app.send_static_file("assets/temp_H.json")

@app.route('/hum_hour')
def hum_hour():
    return app.send_static_file("assets/hum_H.json")

@app.route('/co2_hour')
def co2_hour():
    return app.send_static_file("assets/co2_H.json")

@app.route('/co2_ext_hour')
def co2_ext_hour():
    return app.send_static_file("assets/co2_ext_H.json")

@app.route('/recent')
def recent():
    return app.send_static_file("assets/recent.json")

@app.route('/assets/js/<path:path>')
def send_js(path):
    return send_from_directory("static/assets/js/", path)


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


if __name__ == '__main__':
    app.run(debug=True)
