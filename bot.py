import telebot
from telebot import types
from helpers import token
import json

from db_worker import Users as usr

bot = telebot.TeleBot(token, threaded=False)

tamplate = ['Авторизация для клиентов ВТБ24', 'Операции', 'Перевод']
lor1 = 'доров'
lor2 = 'прив'


def takePayerPN(message):
<<<<<<< HEAD
    if message.chat.id == message.contact.user_id:
        text_info = bot.send_message(message.chat.id, "Нельзя отправить платёж самому себе.")
        bot.register_next_step_handler(text_info, takePayerPN)
    else:
        try:
            contact_id = message.contact.user_id
            phone_number = message.contact.phone_number
            from db_worker import Drafts as drf
            drf.update_last_with_data(message.chat.id, {"RecieverID": contact_id, "RecieverPN": phone_number})
            kb = types.InlineKeyboardMarkup()
            yesBut = types.InlineKeyboardButton(text='Принять', callback_data='yes,{}'.format(message.chat.id))
            noBut = types.InlineKeyboardButton(text='Отклонить', callback_data='no,{}'.format(message.chat.id))
            kb.add(yesBut, noBut)
            bot.send_message(contact_id, 'Для вас есть перевод.'.format(), reply_markup=kb)
            bot.send_message(message.chat.id, 'Запрос отправлен.')
        except:
            bot.send_message(message.chat.id, "Некорректный ввод. Начните с начала.")
=======
    try:
        contact_id = message.contact.user_id
        phone_number = message.contact.phone_number
        from db_worker import Drafts as drf
        drf.update_last_with_data(message.chat.id, {"ReceiverID": contact_id, "ReceiverPN": phone_number})
        kb = types.InlineKeyboardMarkup()
        yesBut = types.InlineKeyboardButton(text='Принять', callback_data='yes,{}'.format(message.chat.id))
        noBut = types.InlineKeyboardButton(text='Отклонить', callback_data='no,{}'.format(message.chat.id))
        kb.add(yesBut, noBut)
        bot.send_message(contact_id, 'Для вас есть перевод.'.format(), reply_markup=kb)
        bot.send_message(message.chat.id, 'Запрос отправлен.')
    except:
        bot.send_message(message.chat.id, "Некорректный ввод. Начните с начала.")
>>>>>>> origin/telegram


def sendSum(message):
    text = message.text.split(",")
    try:
        total = float(text[0])
        from db_worker import Drafts as drf
        drf.new({"PayerID": message.chat.id, "Reason": text[1], "Total": total, })
        text_info = bot.send_message(message.chat.id, "Перешлите контакт пользователя")
        bot.register_next_step_handler(text_info, takePayerPN)
    except:
        bot.send_message(message.chat.id, "Некорректный ввод. Начните с начала.")


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    if usr.get({"@Users": message.chat.id}):
        if (usr.get({"@Users": message.chat.id}))[0]['VTBClient']:
            from datetime import datetime
            try:
                if (usr.get({"@Users": message.chat.id}))[0]['TokenExpires'] < datetime.now():
                    markup.add(*tamplate)
                else:
                    markup.add(*tamplate[1:])
            except:
                markup.add(*tamplate)
        else:
            markup.add('Операции', 'Перевод')
        bot.send_message(message.chat.id, 'Приветствую. Выберите интересующий вас раздел.', reply_markup=markup)
    else:
        markup.add(types.KeyboardButton(text="Отправить номер телефона", request_contact=True))
        bot.send_message(message.chat.id, 'Для работы нам необходим ваш номер телефона', reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def get(message):
    if message.chat.id == message.contact.user_id:
        vtb_user = (message.contact.phone_number, 1)
        not_vtb_user = (message.contact.phone_number, 0)
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="Да", callback_data=str(vtb_user))
        button2 = types.InlineKeyboardButton(text="Нет", callback_data=str(not_vtb_user))
        keyboard.add(button1, button2)
        bot.send_message(message.chat.id, 'Спасибо за доверие вашего телефона.\n Вы являетесь клиентом банка ВТБ?',
                         reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def buttonsSend(message):
    if message.text == 'drop':
        usr.delete(message.chat.id)

    if usr.get({"@Users": message.chat.id}):
        if message.text == "Перевод":
            text_info = bot.send_message(message.chat.id, "Введите сумму и назначение платежа через запятую")
            bot.register_next_step_handler(text_info, sendSum)
        if message.text == 'Авторизация для клиентов ВТБ24':
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Перейти",
                                                    url="http://82.202.199.51/auth?response_type=code&scope=all&client_id=914278823132762424955&redirect_uri=https://tu8fvecqlg.execute-api.us-east-2.amazonaws.com/vtb24/auth&state={}".format(
                                                        message.chat.id))
            keyboard.add(url_button)
            bot.send_message(message.chat.id,
                             "Перейдите по ссылке и введите логин и пароль.",
                             reply_markup=keyboard)

        if message.text == 'Операции':
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

    if call.data.split(",")[0] == "yes":
        sender_id = call.data.split(",")[1]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Спасибо")
        from datetime import datetime
        try:
            if (usr.get({"@Users": sender_id}))[0]['TokenExpires'] < datetime.now():
                markup = types.InlineKeyboardMarkup()
                bt = types.InlineKeyboardButton(text="Подтвердить", callback_data="got_token")
                markup.add(bt)
                bot.send_message(sender_id, "Для завершения операции необходимо авторизоваться в личном кабинете.",
                                 reply_markup=markup)
            else:
                bot.send_message(sender_id, "Перевод совершен.")
        except:
            markup = types.InlineKeyboardMarkup()
            bt = types.InlineKeyboardButton(text="Подтвердить", callback_data="got_token")
            markup.add(bt)
            bot.send_message(sender_id, "Для завершения операции необходимо авторизоваться в личном кабинете.",
                             reply_markup=markup)

    if call.data == "got_token":
        try:
            from datetime import datetime
            if (usr.get({"@Users": call.message.chat.id}))[0]['TokenExpires'] < datetime.now():
                markup = types.InlineKeyboardMarkup()
                bt = types.InlineKeyboardButton(text="Подтвердить", callback_data="got_token")
                markup.add(bt)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Для завершения операции необходимо авторизоваться в личном кабинете.",
                                      reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Перевод совершен.")
        except:
            markup = types.InlineKeyboardMarkup()
            bt = types.InlineKeyboardButton(text="Подтвердить", callback_data="got_token")
            markup.add(bt)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Для завершения операции необходимо авторизоваться в личном кабинете.",
                                  reply_markup=markup)

    if call.data.split(",")[0] == "no":
        sender_id = call.data.split(",")[1]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Спасибо")
        bot.send_message(sender_id, "Перевод отклонен получателем.")

    if eval(call.data)[1]:
        usr.new({"@Users": call.message.chat.id, "PhoneNumber": eval(call.data)[0], "VTBClient": True})
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Поздравляю, регистрация завершена! Вам доступен полный функционал")
        welcome(call.message)

    if not eval(call.data)[1]:
        usr.new({"@Users": call.message.chat.id, "PhoneNumber": eval(call.data)[0], "VTBClient": False})
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Регистрация завершена. Вы не являетесь клиентом банка ВТБ24, ваш функционал урезан.")
        welcome(call.message)


def main(content, some_other_arg):
    print('new request came:\n{}'.format(content))
    print('content param type: {}'.format(type(content)))
    bot.process_new_updates([telebot.types.Update.de_json(json.dumps(content))])
