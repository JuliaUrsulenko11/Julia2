from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater
from telegram import Message
import requests
import sqlite3
import config

conn = sqlite3.connect("my_db.db")
cursor = conn.cursor()
# полученный при регистрации на OpenWeatherMap.org.
app_id = "1ca2b4019db56ec8d72318747452f981"


class bot():
    def add_user(self, chat_id, message):
        cursor.execute("""INSERT INTO chats
                          VALUES (chat_id, message)""")
        conn.commit()


    # Проверка наличия в базе информации о нужном населенном пункте
    def get_city_id(self, s_city_name):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': s_city_name,
                                       'type': 'like',
                                       'units': 'metric',
                                       'lang': 'ru',
                                       'APPID': app_id})
            data = res.json()
            cities = ["{} ({})".format(d['name'], d['sys']['country'])
                      for d in data['list']]
            print("city:", cities)
            city_id = data['list'][0]['id']
            # print('city_id=', city_id)
        except Exception as e:
            print("Exception (find):", e)
            pass
        assert isinstance(city_id, int)
        return city_id


    # Прогноз
    def request_forecast(self, city_id):
        print("2")
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                               params={'id': city_id,
                                       'units': 'metric',
                                       'lang': 'ru',
                                       'APPID': appid})
            data = res.json()
            cc = print('city:', data['city']['name'], data['city']['country'])
            for i in data['list']:
                print((i['dt_txt'])[:16], '{0:+3.0f}'.format(i['main']['temp']),
                      '{0:2.0f}'.format(i['wind']['speed']) + " м/с",
                      get_wind_direction(i['wind']['deg']),
                      i['weather'][0]['description'])
        except Exception as e:
            print("Exception (forecast):", e)
            pass


    def get_wind_direction(self, deg):
        l = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']
        for i in range(0, 8):
            step = 45.
            min = i * step - 45 / 2.
            max = i * step + 45 / 2.
            if i == 0 and deg > 360 - 45 / 2.:
                deg = deg - 360
            if deg >= min and deg <= max:
                res = l[i]
                break
        return res


    def __init__(self, city):
        if len(city) == 2:
            s_city_name = city
            city_id = get_city_id(s_city_name)
        elif len(sys.argv) > 2:
            return config.error
        print("1")
        bot.request_forecast(city_id)


#   FRONT
def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id,
							 text = config.start_message)


def echo(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id,
							 text = config.answer)
    bot(Message.text)
    
print("1234567890")
#   !!! DON'T TOUCH !!!
updater = Updater(token = config.token, use_context = True)

dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
