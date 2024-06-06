from flask import Flask, render_template, request, jsonify
from threading import Thread, Event
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

alarm_time = {'h': None,
              'm': None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global alarm_time
    hour = request.form['hour']
    minute = request.form['minute']
    alarm_time = {'h': int(hour), 'm': int(minute)}
    logging.info(f"Alarm time set to: {alarm_time['h']}:{alarm_time['m']}")
    return jsonify(alarm_time)

@app.route('/get_time', methods=['GET'])
def get_time():
    return jsonify(alarm_time)




def remap(value, from_min, from_max, to_min, to_max):
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

def calc_trig(alarm_time: dict):

    if alarm_time['m'] < 30:
        trig_m = 60 - (30 - alarm_time['m'])
        trig_h = alarm_time['h'] - 1
    else:
        trig_m = alarm_time['m'] - 30
        trig_h = alarm_time['h']
    # Check if hours are negative
    if trig_h < 0:
        trig_h = 23

    trig_t = {'h': trig_h,
              'm': trig_m}
    return trig_t





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

    print("Gradual increase is done, sun will die in 1 hour")
    time.sleep(3600)
    sun(pwm, power=0)
    destroy(pwm, 33)




def check_time(trig_time):

    now = datetime.datetime.now()
    current_t = {'h': now.hour,
                 'm': now.minute}

    if (trig_time['h'] == current_t['h']) and (trig_time['m'] == current_t['m']):
        return True
    else:
        return False

def check_alarm():
    while True:
        if alarm_time['h'] is not None and alarm_time['m'] is not None:
            trig_time = calc_trig(alarm_time)
        while True:
            if check_time(trig_time):
                run_alarm()
                break
            else:
                time.sleep(5)


if __name__ == "__main__":
    alarm_thread = Thread(target=check_alarm)
    alarm_thread.start()
    app.run(debug=True, host='0.0.0.0', port=8080)

    alarm_thread.join()
