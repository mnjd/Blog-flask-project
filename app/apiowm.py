import requests
from pprint import pprint
import re
import psycopg2
from datetime import datetime, date

BASE_URL = 'http://api.openweathermap.org/data/2.5/'
appid = '258dd57f7acfe60c2ccad24e5b228dea'

def generate_endpoint(endpoint):
    return BASE_URL + endpoint

#http://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=APPID

def weather_data(string):
    r = req_data(string)
    if r.json()['cod'] == 401 and re.match(r'^Invalid API key', r.json()['message']):
        raise Exception('Your API Key is invalid')
    else:
        dic = r.json()
        return dic

def req_data(string):
    params = {
        'q': string,
        'appid': appid
        }
    r = requests.get(generate_endpoint('weather'), params=params)
    return r

meteo = weather_data('Paris,fr')

temperature_ressentie = int(13.12 + 0.6215 * float(meteo['main']['temp'] - 273.15) - 11.37 * float(meteo['wind']['speed'] * 3.6) ** 0.16 + 0.3965 * float(meteo['main']['temp'] - 273.15) * float(meteo['wind']['speed'] * 3.6) ** 0.16)


#--------Connection to database--------#
conn = psycopg2.connect(database="blogflask", user="postgres", password="postgres1234")
print('Connected to database')
cur = conn.cursor()


if conn:
    cur.execute("INSERT INTO weatherdb VALUES (%s, %s, %s, %s, %s, %s, %s);", (datetime.now(), meteo['name'], int(round(meteo['main']['temp'] - 273.15)), int(meteo['main']['humidity']), int(meteo['main']['pressure']), temperature_ressentie, meteo['weather'][0]['description']))
    conn.commit()
    print('Table updated')
    conn.close()
    print('Database closed')

#--------------------------------------#