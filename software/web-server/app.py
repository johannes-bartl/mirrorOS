#!/usr/bin/python
from gevent import monkey
monkey.patch_all(Event=False)
import json
import os
import pika
import sys
from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
import argparse
import time
from threading import Thread
from datetime import datetime, timezone
connection,channel = None, None
sys.path.append('/home/spot/Software/mirrorOS/software')

import helper_function as hf
cfg = hf.read_yaml()

app = Flask(__name__)
app.config['SECRET'] = cfg["server"]["flask"]["secret"]
app.config['TEMPLATES_AUTO_RELOAD'] = cfg["server"]["flask"]["templates_auto_reload"]

socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins='*')
bootstrap = Bootstrap(app)

parser = argparse.ArgumentParser(description="Host a webserver: mirrorOS webpage")
parser.add_argument('-v','--verbose', action='store_true', help="enable verbose mode", default=False, dest="verbose")
args = parser.parse_args()


def add_time(message):
    pub = {
        'message': message,
        'time': datetime.now(timezone.utc).isoformat()[:-6] + 'Z'
    }
    return pub

@app.route('/')
def index():
    return render_template(cfg["server"]["flask"]["template"])

@socketio.on('subscribe')
def handle_subscribe():
    pass

@socketio.on('disconnect')
def handle_disconnect():
    print('disconnect')
    pass

def callback(ch, method, properties, body):
    producer,information,topic = method.routing_key.split(".")
    data = dict(
        topic=topic,
        payload=body.decode("utf-8"),
        producer=producer
    )
    if args.verbose:
        print(f'Incoming {information} message: {data}')
    socketio.emit('rmq', data=data)


def consume_messages():
    global connection, channel, queue
    while True:
        try:
            if connection == None or not connection.is_open:
                connection = hf.rbmq_connect()
                channel = connection.channel()
                queue = channel.queue_declare(queue="webserver", durable=True,
                                              arguments={'x-max-length': 1})
                channel.queue_bind(exchange=cfg["server"]["rbmq"]["exchange"], queue=queue.method.queue,
                                   routing_key=cfg["server"]["rbmq"]["routing_key"])

                channel.basic_consume(queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
                channel.start_consuming()
                print('rabbitmq Meta: Start consuming!')
        except Exception as e:
            print(f'rbmq: error when trying to consume: {e}')
            time.sleep(int(cfg["server"]["rbmq"]["check_interval"]))

if __name__ == '__main__':
    print("starting thread 1")
    consumer_thread = Thread(target=consume_messages)
    consumer_thread.start()

    socketio.run(app, host='0.0.0.0', port=80, use_reloader=False, debug=True)

