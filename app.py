from flask import Flask, render_template, request, jsonify
from threading import Thread
from typing import Dict, Optional
import time
import datetime
import RPi.GPIO as GPIO

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
    return jsonify(latest_time)

@app.route('/get_time', methods=['GET'])
def get_time():
    return jsonify(latest_time)




def setup(pwm_pin: int):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pwm_pin, GPIO.OUT)
    GPIO.output(pwm_pin, GPIO.LOW)
    pwm = GPIO.PWM(pwm_pin, 60) # Set frequency to 1 KHz
    pwm.start(0) # Set the starting Duty Cycle
    return pwm

def destroy(pwm, pwm_pin) :
    pwm.stop()
    GPIO.output(pwm_pin, GPIO.LOW)
    GPIO.cleanup()

def sun(pwm, power: int): # Sett light instensity
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

def remap(value, from_min, from_max, to_min, to_max):
    # Convert the value from the original range to a value in the new range
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

import datetime
import time

def check_time():
    while True:
        now = datetime.datetime.now()
        if latest_time['hour'] is not None and latest_time['minute'] is not None:
            alarm_time = datetime.time(latest_time['hour'], latest_time['minute'])
            alarm_datetime = datetime.datetime.combine(datetime.date.today(), alarm_time)

            # Check if alarm time is earlier than current time
            if alarm_datetime < now:
                # Adjust alarm to next day
                alarm_datetime += datetime.timedelta(days=1)

            # Check if it's time to trigger the alarm
            if now >= alarm_datetime:
                print(f"Current time: {now.hour}:{now.minute}\nAlarm time: {latest_time['hour']}:{latest_time['minute']}")
                print("Running alarm")
                run_alarm()

        time.sleep(1)  # Check every second



if __name__ == "__main__":
    # Start the background thread
    setup(33)
    Thread(target=check_time, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=8080)
