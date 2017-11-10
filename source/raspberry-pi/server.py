#!flask/bin/python
from flask import Flask, jsonify, request, make_response, abort, send_from_directory

import plot

app = Flask(__name__, static_url_path='/static')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/update')
def update():
    plot.make_week()
    return app.send_static_file("index.html")

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/hum')
def hum():
    return app.send_static_file("hum.html")

@app.route('/temp')
def temp():
    return app.send_static_file("temp.html")

@app.route('/co2')
def co2():
    return app.send_static_file("co2.html")

@app.route('/last_hour')
def last_hour():
    return app.send_static_file("last_hour.html")

@app.route('/weeks')
def weeks():
    return app.send_static_file("assets/weeks.json")

@app.route('/carbon_dioxide')
def carbon_dioxide():
    return app.send_static_file("assets/co2_days.json")

@app.route('/humidity')
def humidity():
    return app.send_static_file("assets/hum_days.json")

@app.route('/temperature')
def temperature():
    return app.send_static_file("assets/temp_days.json")

@app.route('/temp_hour')
def temp_hour():
    return app.send_static_file("assets/temp_H.json")

@app.route('/hum_hour')
def hum_hour():
    return app.send_static_file("assets/hum_H.json")

@app.route('/co2_hour')
def co2_hour():
    return app.send_static_file("assets/co2_H.json")

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
