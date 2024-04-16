import paho.mqtt.client as mqtt
import yaml
import sys

def parse_dtype(value,type):
    try:
        return type(value)
    except:
        return value

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

#read yaml config
def read_yaml(path):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


# Create an MQTT client & connect to Broker
def on_connect(client,userdata,flags,rc):
    if userdata != None:
        for topic in userdata["topic"]:
            client.subscribe(topic)
            print(f"Subscribed to MQTT topic: {topic}")

def mqtt_connect(cfg,userdata=None):
    client = mqtt.Client(userdata=userdata)
    client.on_connect = on_connect
    conn = client.connect(cfg["server"]["mqtt"]["broker_adress"], int(cfg["server"]["mqtt"]["port"]))
    if conn == 0:
        return client
    else:
        sys.exit()