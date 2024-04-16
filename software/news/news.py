#!/usr/bin/python
import feedparser
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import sys
sys.path.append('/home/spot/Software/mirrorOS/software')
import helper_function as hf
import time
import json
import pika
cfg = hf.read_yaml()

exchange = cfg["server"]["rbmq"]["exchange"]
routing_key = "home.data.news"
connection,channel = None,None

def extract_img_path(html):
    soup = BeautifulSoup(html, 'html.parser')
    img_tag = soup.find('img')
    img_path = img_tag['src']
    return img_path


def get_news(rss_feed_url):
    global connection,channel

    while True:
        try:
            if connection == None or not connection.is_open:
                connection = hf.rbmq_connect()

                channel = connection.channel()
                print('rbmq: connected')


            try:
                # Parse the RSS feed
                feed = feedparser.parse(rss_feed_url,response_headers={'content-type': 'text/xml; charset=utf-8'})
                # Check for any errors during parsing
                if feed.bozo:
                    print("Error parsing RSS feed:", feed.bozo_exception)
                    return

                # Extract and print the information
                data = {}
                for i,entry in enumerate(feed.entries[:cfg["news"]["num_news"]]):
                    data[i] = {
                        "title":entry.title,
                        "link":entry.link,
                        "description":entry.description,
                        "img_path":extract_img_path(entry.content[0].value),
                        "timestamp":entry.published
                    }
                pub = {
                    'message': data,
                    'time': datetime.now(timezone.utc).isoformat()[:-6] + 'Z'
                }
                print(pub)

                channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(pub),
                                      properties=pika.BasicProperties(delivery_mode=2))
                time.sleep(float(cfg["news"]["update"]))
            except Exception as e:
                print(f"Error {e}: failed to parse")

        except Exception as e:
            print(f'rbmq: error when trying to publish: {e}')
            time.sleep(int(cfg["server"]["rbmq"]["check_interval"]))


if __name__ == "__main__":
    get_news(cfg["news"]["rss_feed"])
