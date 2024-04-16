#!/usr/bin/python
import datetime
import json
import time
import sys
sys.path.append('/home/spot/software')
import helper_function as hf
import locale
import sys
# Set the locale to German
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')


cfg = hf.read_yaml("/home/spot/software/cfg/mirror.yaml")
def get_time():
    try:
        client = hf.mqtt_connect(cfg)
    except:
        sys.exit()
    while True:
        now = datetime.datetime.now()
        # Format the time as HH : MM : SS
        time_format = now.strftime("%H : %M : %S")

        # Format the date as "Wochentag, Tag. Monat"
        date_format = now.strftime("%A, %d. %B")

        # Print the formatted time and date
        print(time_format)
        print(date_format)
        time.sleep(float(cfg["clock"]["update"]))
        pub = {
            "time": time_format,
            "date": date_format,
            "hour": f'{now.hour:02d}',
            "minute": f'{now.minute:02d}',
            "second": f'{now.second:02d}',
            "day_of_week": f'{now.strftime("%A")}',
            "day": f'{now.strftime("%d")}',
            "month": f'{now.strftime("%m")}',
            "year": f'{now.strftime("%Y")}',
        }
        try:
            client.publish("clock",json.dumps(pub,ensure_ascii=False))
        except:
            sys.exit()




if __name__ == "__main__":
    get_time()