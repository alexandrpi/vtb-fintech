# import requests
#
# r = requests.get(
#     'http://82.202.199.51/auth?response_type=code&scope=all&client_id=770296883857801006116&redirect_uri=http://127.0.0.1&state=12345')
# print(r.text)

# client_id = "770296883857801006116"
# client_secret = "f70c090fa2c049dea463342338653bde261ce5ddc1d0497c815b542f7ac83299"
# client_host = "127.0.0.1:5000"
#
# url = 'https://<хост сервиса>/auth?response_type=code&scope=all&client_id={}&redirect_uri=REDIRECT_URI&state=RANDOM_STATE'.format(client_id)
# print(url)
#
# import telebot
# from telebot import types
# from helpers import token
#
# bot = telebot.TeleBot(token)
#
#
# bot.remove_webhook()
# bot.set_webhook(url='https://tu8fvecqlg.execute-api.us-east-2.amazonaws.com/vtb24/AAGPAHB7eDP7eXoEe3Zoxqc1uFvTsRahDbU')
tb_user = (89999999999,1)
import sys
import json
z = '{"d": ["7XXXXXXXXXX", 1]}'
a = sys.getsizeof(z)
b = sys.getsizeof(str(tb_user))
print("{} {} {}".format(a,eval(str(tb_user)),tb_user[0]))
