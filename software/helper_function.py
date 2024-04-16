import yaml
import sys
import pika

def parse_dtype(value,type):
    try:
        return type(value)
    except:
        return value

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

#read yaml config
def read_yaml(path="/home/spot/Software/mirrorOS/software/cfg/mirror.yaml"):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)

def rbmq_connect():
    cfg = read_yaml()
    credentials = pika.PlainCredentials(cfg["server"]["rbmq"]["user"], cfg["server"]["rbmq"]["password"])
    connection_parameters = pika.ConnectionParameters(cfg["server"]["rbmq"]["host"],
                                                      cfg["server"]["rbmq"]["port"],
                                                      cfg["server"]["rbmq"]["vhost"],
                                                      credentials)


    return pika.BlockingConnection(connection_parameters)