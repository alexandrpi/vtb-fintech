import telebot
from telebot import types
from helpers import token
import json

bot = telebot.TeleBot(token, threaded=False)

tamplate = ['Авторизация для клиентов ВТБ24', 'операции']
lor1 = 'доров'
lor2 = 'прив'


@bot.message_handler(commands=['start'])
def wellcome(message):
    print('comand')
    # если зареган!!!!!!!!!!!!!!!!!
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    markup.add(*tamplate)
    bot.send_message(message.chat.id, 'Приветствую. Выберите интересующий вас раздел.', reply_markup=markup)
    # иначе !!!!!!!!!!!!!!!!!!!!!!!
    # markup.add(types.KeyboardButton(text="Отправить номер телефона", request_contact=True))
    # bot.send_message(message.chat.id, 'Для работы нам необходим ваш номер телефона', reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def get(message):
    if message.chat.id == message.contact.user_id:
        bot.send_message(message.chat.id, 'Спасибо за доверее вашего телефона')
        # пользователь отправил свой телефон 
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
    print('text')
    if message.text == 'Авторизация для клиентов ВТБ24':
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Перейти",
                                                url="http://82.202.199.51/auth?response_type=code&scope=all&client_id=770296883857801006116&redirect_uri=http://127.0.0.1:5000/vtb&state={}".format(
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
    print(call.data)
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


def main(content, some_other_arg):
    print('new request came:\n{}'.format(content))
    print('content param type: {}'.format(type(content)))
    bot.process_new_updates([telebot.types.Update.de_json(json.dumps(content))])
