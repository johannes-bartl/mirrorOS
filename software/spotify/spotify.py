#!/usr/bin/python
import spotipy
import sys
sys.path.append('/home/spot/Software/mirrorOS/software')
import helper_function as hf
import yaml
from datetime import datetime,timezone
import time
import json
import os
import pika

os.chdir('/home/spot/Software/mirrorOS/software/spotify')

cfg = hf.read_yaml()
lcfg = cfg["spotify"] #access local config for spotify

connection,channel = None, None
routing_key = "home.data.spotify"

auth = {
    'CLIENT_ID': lcfg['client_id'],
    'CLIENT_SECRET': lcfg['client_secret'],
    'REDIRECT_URI' : lcfg["redirect_uri"],
    'SCOPE': lcfg["scope"]
}

def authorize(auth,cfg):
    auth_manger = spotipy.oauth2.SpotifyOAuth(
        client_id=auth["CLIENT_ID"],
        client_secret=auth["CLIENT_SECRET"],
        redirect_uri=auth["REDIRECT_URI"],
        scope=auth["SCOPE"]
    )


    token_info = auth_manger.get_cached_token()

    if not token_info:
        auth_url = auth_manger.get_authorize_url()
        print("Please visit this URL to authenticate:", auth_url)
        response = input("Enter the URL you were redirected to: ")
        code = auth_manger.parse_response_code(response)
        token_info = auth_manger.get_access_token(code)

        # cfg["spotify"]["refresh_token"] = token_info["refresh_token"]
        # with open(cfg_path, 'w') as yaml_file:
        #     yaml.dump(cfg, yaml_file, default_flow_style=False)

        return token_info

    elif token_info:
        if token_info["expires_at"]-datetime.now().timestamp() < 10:
            print('Refresh Token')
            return auth_manger.refresh_access_token(token_info["refresh_token"])
        else:
            return token_info

def get_spotify():
    global connection
    while True:
        try:
            if connection == None or not connection.is_open:
                connection = hf.rbmq_connect()

                channel = connection.channel()
                print('rbmq: connected')

            #currently playing
            token_info = authorize(auth,cfg)
            sp = spotipy.Spotify(auth=token_info["access_token"])
            cp = sp.current_playback()
            print(cp)
            if cp != None:
                current_playback = {
                    'now_playing': 1,
                    'device_name': cp["device"]["name"],
                    'device_type': cp["device"]["type"],
                    'shuffle_state': cp["shuffle_state"],
                    'repeat_state': cp["repeat_state"],
                    'type': cp["context"]["type"],
                    'progress_ms': cp["progress_ms"],
                    'duration': cp["item"]["duration_ms"],
                    'artists': cp["item"]["artists"][0]["name"],
                    'progress': 100 * float(cp["progress_ms"] / cp["item"]["duration_ms"]),
                    'cover_img': cp["item"]["album"]["images"][0]["url"],
                    'title': cp["item"]["name"]
                }
            else:
                current_playback = {
                    'now_playing': 0
                }

            pub = {
                'message': current_playback,
                'time': datetime.now(timezone.utc).isoformat()[:-6] + 'Z'
            }
            channel.basic_publish(exchange=cfg["server"]["rbmq"]["exchange"], routing_key=routing_key, body=json.dumps(pub),
                                  properties=pika.BasicProperties(delivery_mode=2))
            time.sleep(float(cfg["spotify"]["update"]))

        except Exception as e:
            print(f'rbmq: error when trying to publish: {e}')
            time.sleep(int(cfg["server"]["rbmq"]["check_interval"]))
if __name__ == "__main__":
    get_spotify()


