import telebot
from telebot import types
from helpers import token
import json

from db_worker import Users as usr

bot = telebot.TeleBot(token, threaded=False)

tamplate = ['Авторизация для клиентов ВТБ24', 'операции']
lor1 = 'доров'
lor2 = 'прив'


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    if usr.get({"@Users": message.chat.id}):
        if (usr.get({"@Users": message.chat.id}))[0]['VTBClient']:
            markup.add(*tamplate)
        else:
            markup.add('операции')
        bot.send_message(message.chat.id, 'Приветствую. Выберите интересующий вас раздел.', reply_markup=markup)
    else:
        markup.add(types.KeyboardButton(text="Отправить номер телефона", request_contact=True))
        bot.send_message(message.chat.id, 'Для работы нам необходим ваш номер телефона', reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def get(message):
    print("{} {}".format(message.chat.id, message.contact.user_id))
    if message.chat.id == message.contact.user_id:
        usr.new({"@Users": message.chat.id, "PhoneNumber": message.contact.phone_number, "VTBClient": False})
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="Да", callback_data="flag_True")
        button2 = types.InlineKeyboardButton(text="Нет", callback_data="flag_False")
        keyboard.add(button1, button2)
        bot.send_message(message.chat.id, 'Спасибо за доверие вашего телефона.\n Вы являетесь клиентом банка ВТБ?',
                         reply_markup=keyboard)
    else:  # отправил номер того кому хочет бабки перевести
        try:
            contact_id = message.contact.user_id
            phone_number = message.contact.phone_number
            bot.send_message(contact_id, 'для вас есть перевод.')
        except:
            pass
            # отправка смсс сообщения


@bot.message_handler(content_types=["text"])
def buttonsSend(message):
    if message.text == 'хуй':
        usr.delete(message.chat.id)
    if message.text == 'хуй1':
        a = usr.get({"@Users": message.chat.id})
        bot.send_message(message.chat.id, str(a[0]['VTBClient']))

    if usr.get({"@Users": message.chat.id}):
        if message.text == 'Авторизация для клиентов ВТБ24':
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Перейти",
                                                    url="http://82.202.199.51/auth?response_type=code&scope=all&client_id=914278823132762424955&redirect_uri=https://tu8fvecqlg.execute-api.us-east-2.amazonaws.com/vtb24/auth&state={}".format(
                                                        message.chat.id))
            keyboard.add(url_button)
            bot.send_message(message.chat.id,
                             "Перейдите по ссылке и введите логин и пароль.",
                             reply_markup=keyboard)

        if message.text == 'операции':
            kb = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text='туда', callback_data='left')
            kb.add(button)
            bot.send_message(message.chat.id, lor1, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "left":
        kb = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='сюда', callback_data='right')
        kb.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=lor2,
                              reply_markup=kb)

    if call.data == "right":
        kb = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='туда', callback_data='left')
        kb.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=lor1,
                              reply_markup=kb)

    if call.data == "flag_True":
        usr.update_with_data(call.message.chat.id, {"VTBClient": True})

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Поздравляю, регистрация завершена! Вам доступен полный функционал")
        welcome(call.message)

    if call.data == "flag_False":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Регистрация завершена. Вы не являетесь клиентом банка ВТБ24, ваш функционал урезан.")
        welcome(call.message)

def main(content, some_other_arg):
    print('new request came:\n{}'.format(content))
    print('content param type: {}'.format(type(content)))
    bot.process_new_updates([telebot.types.Update.de_json(json.dumps(content))])
