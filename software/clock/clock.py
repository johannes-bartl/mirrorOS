#!/usr/bin/python
from datetime import datetime,timezone
import json
import time
import sys
sys.path.append('/home/spot/Software/mirrorOS/software')
import helper_function as hf
import sys
import pika

import locale
# Set the locale to German
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')


cfg = hf.read_yaml()
exchange = cfg["server"]["rbmq"]["exchange"]
routing_key = "home.data.clock"
connection,channel = None,None
def get_time():
    global connection
    while True:
        try:
            if connection == None or not connection.is_open:
                connection = hf.rbmq_connect()


                channel = connection.channel()
                print('rbmq: connected')

            now = datetime.now()
            # Format the time as HH : MM : SS
            time_format = now.strftime("%H : %M : %S")

            # Format the date as "Wochentag, Tag. Monat"
            date_format = now.strftime("%A, %d. %B")

            # Print the formatted time and date
            time.sleep(float(cfg["clock"]["update"]))
            data = {
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

            pub = {
                'message': data,
                'time': datetime.now(timezone.utc).isoformat()[:-6] + 'Z'
            }
            print(pub)
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(pub),
                                  properties=pika.BasicProperties(delivery_mode=2))
            print('published via rbmq')

        except Exception as e:
            print(f'rbmq: error when trying to publish: {e}')
            time.sleep(int(cfg["server"]["rbmq"]["check_interval"]))



if __name__ == "__main__":
    get_time()