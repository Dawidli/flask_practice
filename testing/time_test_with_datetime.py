import datetime
import time


# Calc time
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


def main():
    alarm_t = {'h': 14,
               'm': 22}
    current_t = {'h': None,
                 'm': None}
    now = datetime.datetime.now()
    current_t['h'] = now.hour
    current_t['m'] = now.minute

    trig_time = calc_trig(alarm_t)

    print(f'Current time : {current_t["h"]}:{current_t["m"]}')
    print(f'Alarm time   : {alarm_t["h"]}:{alarm_t["m"]}')
    print(f'Trigger time : {trig_time["h"]}:{trig_time["m"]}')

    if (trig_time['h'] == current_t['h']) and (trig_time['m'] == current_t['m']):
        print("\nAlarm is being triggered! :D")


if __name__ == '__main__':
    main()