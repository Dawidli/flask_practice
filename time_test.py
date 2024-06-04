import datetime
import time

# Set the alarm time
alarm_time = {
    'hour': 7,
    'minute': 0
}

# Calculate the pre-alarm time (30 minutes before the alarm time)
pre_alarm_time = (datetime.datetime.combine(datetime.date.today(), datetime.time(alarm_time['hour'], alarm_time['minute'])) - datetime.timedelta(minutes=30)).time()

print(f"Alarm time: {alarm_time['hour']}:{alarm_time['minute']:02d}")
print(f"Pre-alarm time: {pre_alarm_time.hour}:{pre_alarm_time.minute:02d}")

# Function to check if current time matches the pre-alarm time
def check_pre_alarm():
    now = datetime.datetime.now().time()
    print(f"Time now: {now.hour}:{now.minute:02d}")
    return now.hour == pre_alarm_time.hour and now.minute == pre_alarm_time.minute

# Main loop to wait for the pre-alarm time
while True:
    if check_pre_alarm():
        print("Pre-alarm time reached! Event happening now.")
        # Place your event code here
        break  # Exit the loop after the event happens
    else:
        print("Waiting for the pre-alarm time to match...")
        time.sleep(30)  # Sleep for 30 seconds before checking again
