#!/usr/bin/python
import json
import os
import sys
import eventlet
from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

sys.path.append('/home/spot/software')
print(sys.path)
import helper_function as hf

cfg = hf.read_yaml("/home/spot/software/cfg/mirror.yaml")

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = cfg["server"]["flask"]["secret"]
app.config['TEMPLATES_AUTO_RELOAD'] = cfg["server"]["flask"]["templates_auto_reload"]
app.config['MQTT_BROKER_URL'] = cfg["server"]["mqtt"]["broker_adress"]
app.config['MQTT_BROKER_PORT'] = int(cfg["server"]["mqtt"]["port"])  # default port for non-tls connection
app.config['MQTT_USERNAME'] = cfg["server"]["mqtt"]["username"]  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = cfg["server"]["mqtt"]["password"]  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = int(cfg["server"]["mqtt"]["keepalive"])  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = cfg["server"]["mqtt"]["tls_enables"]  # set TLS to disabled for testing purposes

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('indexv2.html')

@socketio.on('subscribe')
def handle_subscribe():
    topic = ["weather","spotify","news","clock"]
    for t in topic: mqtt.subscribe(t);

@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(message)
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(data,'-------------------------')
    socketio.emit('mqtt_message', data=data)



# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#     print(level, buf)



if __name__ == '__main__':
    socketio.run(app, host='192.168.0.138', port=80, use_reloader=False, debug=True)