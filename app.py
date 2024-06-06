from flask import Flask, render_template, request, jsonify
from threading import Thread, Event
import datetime
import time
import RPi.GPIO as GPIO
import logging
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set up logging
log_file_path = os.path.join(script_dir, 'app.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

alarm_time = {'h': None, 'm': None}
stop_event = Event()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global alarm_time
    data = request.get_json()
    hour = data.get('hour')
    minute = data.get('minute')
    if hour is not None and minute is not None:
        try:
            alarm_time = {'h': int(hour), 'm': int(minute)}
            logging.info(f"Alarm time set to: {alarm_time['h']}:{alarm_time['m']}")
            return jsonify(alarm_time)
        except ValueError:
            logging.error("Invalid time format received.")
            return jsonify({'error': 'Invalid time format'}), 400
    else:
        logging.error("Missing hour or minute in request.")
        return jsonify({'error': 'Missing hour or minute'}), 400

@app.route('/get_time', methods=['GET'])
def get_time():
    return jsonify(alarm_time)

def remap(value, from_min, from_max, to_min, to_max):
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

def calc_trig(al
