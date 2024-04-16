#!/usr/bin/python
from datetime import datetime, timezone
import time
import requests
import sys
sys.path.append('/home/spot/Software/mirrorOS/software')
import helper_function as hf
import json
import pika


cfg = hf.read_yaml()
auth = f"?lat={cfg['weather']['latitude']}&lon={cfg['weather']['longitude']}&appid={cfg['weather']['key']}"
url =  f"https://api.openweathermap.org/data/2.5/"


exchange = cfg["server"]["rbmq"]["exchange"]
routing_key = "home.data.weather"
connection,channel = None,None

def get_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code: {response.status_code}", url)

def get_weather_condition(code,dic):
    for condition, codes_list in dic.items():
        if code in codes_list:
            return condition
    return None  # Return None if no match is found
def to_c(temp_k):
    return temp_k - 273.15
def get_current():
    url_current = url + "weather" + auth
    current = get_json(url_current)
    progress = 100 * (datetime.now().timestamp() - current["sys"]["sunrise"])/(current["sys"]["sunset"] - current["sys"]["sunrise"])
    day = 1
    if not (progress > 0) & (progress < 100):
        progress = -1
        day = 0

    condition_id = int(current["weather"][0]["id"])

    weather_condition = {
        'thunderstorm': [200, 201, 202, 210, 211, 212, 221, 230, 231, 232],
        'rain': [300, 301, 302, 310, 311, 312, 313, 314, 321, 500, 501, 502, 503, 504, 511, 520, 521, 522, 531],
        'snow': [600, 601, 602, 611, 612, 615, 616, 620, 621, 622],
        'atmosphere': [701, 711, 721, 731, 741, 751, 761, 762, 771, 781],
        'clear': [800],
        'few_clouds': [801],
        'clouds': [802, 803, 804]
    }
    code = get_weather_condition(condition_id,weather_condition)


    pub = {'current': {
        'condition' : current["weather"][0]["main"],
        'condition_id': condition_id,
        'description': current["weather"][0]["description"],
        'temp_c': round(to_c(current["main"]["temp"])),
        'temp_min_c': round(to_c(current["main"]["temp_min"])),
        'temp_max_c': round(to_c(current["main"]["temp_max"])),
        'humidity': current["main"]["humidity"],
        'wind': current["wind"]["speed"],
        'dt': current["dt"],
        'sunrise': current["sys"]["sunrise"],
        'sunset': current["sys"]["sunset"],
        'progress': progress,
        'code': 'clear',
        'day': 0,
    }}
    return pub

def get_today():
    url_today = url + "forecast/hourly" + auth
def get_week():
    url_week = url + "forecast/daily" + auth


def get_weather():
    global connection, channel
    while True:
        try:
            if connection == None or not connection.is_open:
                connection = hf.rbmq_connect()


                channel = connection.channel()
                print('rbmq: connected')

            data = get_current()
            pub = {
                'message': data,
                'time': datetime.now(timezone.utc).isoformat()[:-6] + 'Z'
            }
            print(pub)
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(pub),
                                  properties=pika.BasicProperties(delivery_mode=2))
            time.sleep(float(cfg["weather"]["update"]))

        except Exception as e:
            print(f'rbmq: error when trying to publish: {e}')
            time.sleep(int(cfg["server"]["rbmq"]["check_interval"]))

if __name__ == "__main__":
    get_weather()

'http://maps.openweathermap.org/maps/2.0/weather/PA0/9/511/511&appid=2fb810348b71df638e3d6d0fed4111d8'
"http://maps.openweathermap.org/maps/2.0/weather/PA0/9/1/1?date=1552861800&appid=2fb810348b71df638e3d6d0fed4111d8"
"https://api.openweathermap.org/data/2.5/weather/?lat=49.583332&lon=11.016667&appid=2fb810348b71df638e3d6d0fed4111d8"

'''
    # url's for current weather condtion and forecast 5day every 3hours and 16 days
    url_condition = 'http://api.openweathermap.org/data/2.5/' + 'weather' + '?q=' + city + '&appid=' + key
    url_hourly = 'http://api.openweathermap.org/data/2.5/' + 'forecast' + '?q=' + city + '&appid=' + key
    url_forecast = 'http://api.openweathermap.org/data/2.5/' + 'forecast/daily' + '?q=' + city + '&appid=' + key

    # print(url_condition,url_forecast)

    # get json data from urls

    with urllib.request.urlopen(url_condition) as url:
        condition_json = json.loads(url.read().decode())
    with urllib.request.urlopen(url_hourly) as url:
        hourly_json = json.loads(url.read().decode())
    with urllib.request.urlopen(url_forecast) as url:
        forecast_json = json.loads(url.read().decode())

    # initalize dictionary for conditon data
    condition_data = {}
    condition_data['city'] = city
    # --------------------------------------------------------------------------------#
    # temperatures: current / max / min von K in C
    current_temp = condition_json['main']['temp'] - 273.15
    max_temp = condition_json['main']['temp_max'] - 273.15
    min_temp = condition_json['main']['temp_min'] - 273.15

    # openweathermap condition id lists

    weather_condition = {
        'thunderstorm': [200, 201, 202, 210, 211, 212, 221, 230, 231, 232],
        'rain': [300, 301, 302, 310, 311, 312, 313, 314, 321, 500, 501, 502, 503, 504, 511, 520, 521, 522, 531],
        'snow': [600, 601, 602, 611, 612, 615, 616, 620, 621, 622],
        'atmosphere': [701, 711, 721, 731, 741, 751, 761, 762, 771, 781],
        'clear': [800],
        'few_clouds': [801],
        'clouds': [802, 803, 804]
    }

    # return the key of the dict where lookup is in
    def search_dict(dic, lookup):
        for key, val in dic.items():
            if lookup in val:
                return key
        return None

    # pass the condition key through
    condition_data['condition'] = search_dict(weather_condition, condition_json['weather'][0]['id'])

    condition_data['current_temp'] = '{:.1f}'.format(current_temp)
    condition_data['max_temp'] = int(max_temp)
    condition_data['min_temp'] = int(min_temp)

    # sunrise and sunset
    sunrise_unix = condition_json['sys']['sunrise'] + 3600
    sunset_unix = condition_json['sys']['sunset'] + 3600
    # unix time code to datetime
    sunrise = datetime.utcfromtimestamp(sunrise_unix).strftime('%H:%M')
    sunset = datetime.utcfromtimestamp(sunset_unix).strftime('%H:%M')

    condition_data['sunrise'] = sunrise
    condition_data['sunset'] = sunset

    # sunprogress
    current_time = time.time() + 3600
    sun_progress = (current_time - sunrise_unix) / (sunset_unix - sunrise_unix) * 100

    condition_data['sun_progress'] = sun_progress
    # check if current time is between sunrise and sunset
    now = datetime.now()

    if (now > datetime.utcfromtimestamp(sunrise_unix)) & (now < datetime.utcfromtimestamp(sunset_unix)):
        condition_data['isday'] = True
    else:
        condition_data['isday'] = False

    # Test area of the weather

    # condition_data['condition'] = 'clear'
    # condition_data['isday'] = True

    print(condition_data)

    # --------------------------------------------------------------------------------#
    # hourly forecast for 24h
    hourly_data = {}
    f_time24 = []
    f_temp24 = []
    # get all temperatures for the next 24h and save in dict
    for item in hourly_json['list']:
        dt = item['dt'] + 3600
        f_time24.append(datetime.utcfromtimestamp(dt).strftime('%H'))
        f_temp24.append(int(item['main']['temp'] - 273.15))

    hourly_data['time24'] = f_time24[:24]
    hourly_data['temp24'] = f_temp24[:24]

    print(hourly_data)
    # --------------------------------------------------------------------------------#
    # forecast for the next n days including today
    n = 5

    forecast_data = {}

    next_days = []
    temps = []
    min_temps = []
    max_temps = []
    condition_ids = []
    forecast_n_days = []
    for item in forecast_json['list'][1:n + 1]:
        forecast_one_day = []
        # unix time code and transform into string "Morgen,Montag,.."
        days_of_week = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag',
                        'Samstag']  # evtl directly in german with %
        day_unix = item['dt']
        day = datetime.utcfromtimestamp(day_unix).strftime('%w')
        day = days_of_week[int(day)]
        # next_days.append(day)
        forecast_one_day.append(day)
        # current temp + max + min
        temp = int(item['temp']['day'] - 273.15)
        forecast_one_day.append(temp)
        # temps.append(temp)
        min_temp = int((item['temp']['min'] - 273.15))
        # min_temps.append(min_temp)
        forecast_one_day.append(min_temp)
        max_temp = int(item['temp']['max'] - 273.15)
        # max_temps.append(max_temp)
        forecast_one_day.append(max_temp)
        # get condition id
        condition_id = search_dict(weather_condition, item['weather'][0]['id'])
        forecast_one_day.append(condition_id)
        # condition_ids.append(condition_id)

        forecast_n_days.append(forecast_one_day)
    # change the first entry from next_days to 'Morgen'
    # next_days[0] = 'Morgen'
    forecast_n_days[0][0] = 'Morgen'

    print(forecast_n_days)
    # forecast_data['day'] = next_days
    # forecast_data['current_temp'] = temps
    # forecast_data['min_temp'] = min_temps
    # forecast_data['max_temp'] = max_temps
    # forecast_data['condition_id'] = condition_ids

    # print(forecast_data)
    context = {
        'current_condition': condition_data,
        'hourly': hourly_data,
        'forecast': forecast_n_days,
    }
    print(context['current_condition']['sun_progress'])

    # url = 'http://api.wunderground.com/api/64263d62946b83b2/conditions/q/49.7213064,11.0698834.json'
    # weather_json = requests.get(url).json()

    # weather_data = []

    # weather = {
    # 	'city' : weather_json['current_observation']['display_location']['city'],
    # 	'temperature' : weather_json['current_observation']['temp_c'],
    # 	'condition' : weather_json['current_observation']['weather'],
    # 	'icon' : weather_json['current_observation']['icon_url']
    # }
    # weather_data.append(weather)
    # print (weather)
    # context = {"weather_data" : weather_data }

    return render(request, 'weather/index.html', context)

        '''