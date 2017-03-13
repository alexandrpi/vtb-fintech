import telebot
from telebot import types
from financial_db_worker import helpers
import financial_db_worker.db_worker as fdbw

"""АРТЕМА КУСОК"""

bot = telebot.TeleBot(helpers.token)
conn = fdbw.FDBWorker()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    markup.add('создать', 'удалить', 'проверить', 'ахуенные истории')
    msg = bot.reply_to(message, 'ну поехали', reply_markup=markup)
    bot.register_next_step_handler(msg, process_step)


@bot.message_handler(content_types=["text"])
def process_step(message):
    chat_id = message.chat.id
    if message.text == 'создать':
        try:
            conn.create_user('test1', 50000)
            bot.send_message(message.chat.id, text="ты создал юзера")
        except:
            bot.send_message(message.chat.id, text="АААААААААААААААНУКАКОЙ ЖЕ ТЫ МУДАК. пользователь уже создан")
        print(1)

    elif message.text == 'удалить':
        try:
            conn.user_delete('test1')
            bot.send_message(message.chat.id, text="ты удалил юзера")
        except:
            bot.send_message(message.chat.id,
                             text="пользователя не... оххх блять, ну за что мне всё этого? Когда нибудь ты подохнешь мразота ебаная, а я буду смотреть, как ты мучаешься, пидор дырявый. Нельзя удалить того чего нет. Всё Пошел на хуй!")
        print(2)

    elif message.text == 'проверить':
        print(3)
        bot.send_message(message.chat.id, text=str(conn.user_exist('test1')))

    elif message.text == 'ахуенные истории':
        f = open('m.ogg', 'rb')
        bot.send_audio(message.chat.id,f, """this place isn't yours anymore""")

# @bot.message_handler(content_types=["text"])
# def trak(message):
#     # for file in os.listdir("music"):
#     #     if file.split(".")[-1] == "ogg":
#     #         f = open('music/' + file, 'rb')
#     #         res = bot.send_voice(message.chat.id, f, None)
#     # time.sleep(3)
#
#     # bot.send_message(message.chat.id, text="Однако ты пидор")
#     print(message.text)
#     print(message)
#     # print(message.last_name)
if __name__ == '__main__':
    bot.polling(none_stop=True)
