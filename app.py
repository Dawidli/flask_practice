from flask import Flask, render_template, request, jsonify
from threading import Thread
from typing import Dict, Optional
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
latest_time: Dict[str, Optional[int]] = {'hour': None, 'minute': None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global latest_time
    hour = request.form['hour']
    minute = request.form['minute']
    latest_time = {'hour': int(hour), 'minute': int(minute)}
    logging.info(f"Alarm time set to: {latest_time['hour']}:{latest_time['minute']}")
    return jsonify(latest_time)

@app.route('/get_time', methods=['GET'])
def get_time():
    return jsonify(latest_time)

def setup(pwm_pin: int):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pwm_pin, GPIO.OUT)
    GPIO.output(pwm_pin, GPIO.LOW)
    pwm = GPIO.PWM(pwm_pin, 60)  # Set frequency to 60 Hz
    pwm.start(0)  # Set the starting Duty Cycle
    return pwm

def destroy(pwm, pwm_pin):
    pwm.stop()
    GPIO.output(pwm_pin, GPIO.LOW)
    GPIO.cleanup()

def sun(pwm, power: int):
    pwm.ChangeDutyCycle(power)
    time.sleep(0.01)

def run_alarm():
    pwm = setup(33)
    for i in range(1800):
        brightness = remap(i, 0, 1800, 30, 100)
        sun(pwm, power=brightness)
        time.sleep(1)
    logging.info("Gradual increase is done, sun will die in 1 hour")
    time.sleep(3600)
    sun(pwm, power=0)
    destroy(pwm, 33)

def remap(value, from_min, from_max, to_min, to_max):
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

def check_time():
    while True:
        if latest_time['hour'] is not None and latest_time['minute'] is not None:
            now = datetime.datetime.now()
            logging.debug(f"Current time: {now}")  # Log the current time
            alarm_time = datetime.time(latest_time['hour'], latest_time['minute'])
            alarm_datetime = datetime.datetime.combine(datetime.date.today(), alarm_time)

            # Check if alarm time is earlier than current time
            if alarm_datetime < now:
                # Adjust alarm to next day
                alarm_datetime += datetime.timedelta(days=1)

            # Calculate the time to start the alarm (2 minutes before the set time for quick testing)
            start_time = alarm_datetime - datetime.timedelta(minutes=2)
            logging.debug(f"Alarm time: {alarm_datetime}")  # Log the alarm time
            logging.debug(f"Start time: {start_time}")  # Log the start time

            # Check if it's time to trigger the alarm
            if now >= start_time:
                logging.info(f"Running alarm at: {now}")  # Log when the alarm is triggered
                run_alarm()
                latest_time['hour'] = None  # Reset the alarm after it has triggered
                latest_time['minute'] = None

        time.sleep(1)  # Check every second


if __name__ == "__main__":
    # Start the background thread
    setup(33)
    Thread(target=check_time, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=8080)
