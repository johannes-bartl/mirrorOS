#!/usr/bin/python
import spotipy
import sys
sys.path.append('/home/spot/software')
import helper_function as hf
import yaml
import datetime
import time
import json
import os
os.chdir('/home/spot/software/spotify')

cfg_path = "/home/spot/software/cfg/mirror.yaml"
cfg = hf.read_yaml(cfg_path)
lcfg = cfg["spotify"] #access local config for spotify


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
        if token_info["expires_at"]-datetime.datetime.now().timestamp() < 10:
            print('Refresh Token')
            return auth_manger.refresh_access_token(token_info["refresh_token"])
        else:
            return token_info

def get_spotify():
    client = hf.mqtt_connect(cfg)
    while True:

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

        pub = {'current_playback':current_playback}
        client.publish("spotify", json.dumps(pub))
        time.sleep(float(cfg["spotify"]["update"]))

if __name__ == "__main__":
    get_spotify()


