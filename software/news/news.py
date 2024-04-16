#!/usr/bin/python
import feedparser
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('/home/spot/software')
import helper_function as hf
import time
import json

cfg = hf.read_yaml("/home/spot/software/cfg/mirror.yaml")

def extract_img_path(html):
    soup = BeautifulSoup(html, 'html.parser')
    img_tag = soup.find('img')
    img_path = img_tag['src']
    return img_path


def get_news(rss_feed_url):
    client = hf.mqtt_connect(cfg)

    while True:
        try:
            # Parse the RSS feed
            feed = feedparser.parse(rss_feed_url,response_headers={'content-type': 'text/xml; charset=utf-8'})
            # Check for any errors during parsing
            if feed.bozo:
                print("Error parsing RSS feed:", feed.bozo_exception)
                return

            # Extract and print the information
            pub = {}
            for i,entry in enumerate(feed.entries[:cfg["news"]["num_news"]]):
                pub[i] = {
                    "title":entry.title,
                    "link":entry.link,
                    "description":entry.description,
                    "img_path":extract_img_path(entry.content[0].value),
                    "timestamp":entry.published
                }

            client.publish("news",json.dumps(pub,ensure_ascii=False))
            time.sleep(float(cfg["news"]["update"]))
        except KeyboardInterrupt:
            print('Interrupted')
            sys.exit(0)
        except Exception as e:
            print("An error occurred:",e)


if __name__ == "__main__":
    get_news(cfg["news"]["rss_feed"])
