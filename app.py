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

alarm_time: Dict[str, Optional[int]] = {'hour': None, 'minute': None, 'duration':None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global alarm_time, trig_time
    hour = request.form['hour']
    minute = request.form['minute']
    duration = int(request.form['duration'])
    alarm_time = {'hour': int(hour), 'minute': int(minute), 'duration': int(duration)}
    logging.info(f"Alarm time set to: {alarm_time['hour']}:{alarm_time['minute']}")
    trig_time = calc_trig(alarm_time)
    return jsonify(alarm_time)

@app.route('/get_time', methods=['GET'])
def get_time():
    return jsonify(alarm_time)

def remap(value, from_min, from_max, to_min, to_max):
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

def calc_trig(alarm_time: dict):
    if alarm_time['minute'] < 30:
        trig_m = 60 - (30 - alarm_time['minute'])
        trig_h = alarm_time['hour'] - 1
    else:
        trig_m = alarm_time['minute'] - 30
        trig_h = alarm_time['hour']
    # Check if hours are negative
    if trig_h < 0:
        trig_h = 23

    trig_t = {'hour': trig_h, 'minute': trig_m}
    logging.info(f"Trigger time calculated to: {trig_h}:{trig_m}")
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
    dur = alarm_time['duration']*60
    for i in range(dur):
        brightness = remap(i, 0, dur, 30, 100)
        sun(pwm, power=brightness)
        time.sleep(1)
    logging.info("Gradual increase is done, sun will die in 1 hour")
    sleep_time = 3600 * 2
    time.sleep(sleep_time)
    sun(pwm, power=0)

def check_time(trig_time):
    now = datetime.datetime.now()
    current_t = {'hour': now.hour, 'minute': now.minute}
    logging.info(f"Current time is: {current_t['hour']}:{current_t['minute']}")
    return (trig_time['hour'] == current_t['hour']) and (trig_time['minute'] == current_t['minute'])

def check_alarm():
    logging.info("Check_alarm started")
    while True:
        if alarm_time['hour'] is not None and alarm_time['minute'] is not None:
            logging.info("Alarm time is detected to be not NONE")
            logging.info("Performing calc_trig(alarm_time)")
            logging.info(f"Trigger time is {trig_time['hour']}:{trig_time['minute']}")
            while True:
                logging.info("Checking if trigger time matches current time")
                if check_time(trig_time):
                    logging.info(f"Trig matches current, running alarm()")
                    run_alarm()
                    logging.info("Alarm finished breaking inner while loop")
                    break
                else:
                    time.sleep(5)
        else:
            time.sleep(1)

if __name__ == "__main__":
    alarm_thread = Thread(target=check_alarm)
    alarm_thread.start()
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        pass
    finally:
        alarm_thread.join()
        logging.info("Application stopped.")
