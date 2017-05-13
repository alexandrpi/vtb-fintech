# -*- coding: utf-8 -*-

import telebot
from telebot import types
from financial_db_worker import helpers
import financial_db_worker.db_worker as fdbw

"""АРТЕМА КУСОК"""

bot = telebot.TeleBot(helpers.token)
conn = fdbw.FDBWorker()
categories = fdbw.CategoriesWorker(conn, 'test_user')
sours = categories.get_categories()
parentButtons = set([x['Parent'] for x in sours])
childButtons = [x['Name'] for x in sours]
type_id = None
cat_id = None
conn.close()
statisticButtons = {'Расходы': -1, 'Доходы': 1}


# print(statisticButtons.keys())


# print(dataCategories)
# [print(x['Parent']) for x in dataCategories]
# a = set([x["Parent"] for x in a])
# buttons = {x['Name']: x['Parent'] for x in dataCategories}
# print(buttons)
# [print(x) for x in buttons if x["Parent"] == 'Расчеты за услуги и другие операции']

def first_keyboard(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    markup.add('Занесение информации о финансовой операции', 'Проверить состояние счета', 'Финансовая отчетность')
    bot.send_message(message.chat.id,
                     'Привет, ' + message.chat.first_name + '\n \nВыберите пункт меню в зависимости от того, что вы хотите получить или сделать',
                     reply_markup=markup)


def regist(message):
    try:
        conn = fdbw.FDBWorker()
        conn.create_user(str(message.chat.id), float(message.text))
        first_keyboard(message)
    except:
        regist_message = bot.send_message(message.chat.id, 'Некорректный ввод суммы, попробуйтей снова')
        bot.register_next_step_handler(regist_message, regist)


def operation_send(message):
    bot.send_message(message.chat.id, 'Операция выполняется')
    try:
        conn = fdbw.FDBWorker()
        global type_id
        ops = fdbw.OperationsWorker(conn, message.chat.id)
        ops.add_operation(total=message.text, category_id=type_id)
        bot.send_message(message.chat.id, 'Выполнено')
        conn.close()
    except:
        bot.send_message(message.chat.id, 'Некорректный ввод суммы, попробуйтей снова')


# z = [{'Name': 'Выплата по кредиту', 'CategoryTotal': 500.0}, {'Name': 'Получен кредит', 'CategoryTotal': 10000.0}]
# x = [x['Name'] + ": " + str(x['CategoryTotal']) + '\n' for x in z]
# print(x)
# y = ''
# for x in x:
#     y += x
# print(y)
# print(z[0])
# cat_id = 1
# a = [x for x in statisticButtons if x == cat_id]
# print(a)
# print(cat_id)


def financial_analysis(message):
    try:
        date = message.text.split(',')
        conn = fdbw.FDBWorker()
        analysisOperation = fdbw.OperationsWorker(conn, message.chat.id)
        if len(date) == 1:
            analysisResult = analysisOperation.get_by_cat_type(date=date[0], cat_type=cat_id)
        else:
            analysisResult = analysisOperation.get_by_cat_type(start_date=date[0], end_date=date[1], cat_type=cat_id)
        analysisText = [x['Name'] + ": " + str(x['CategoryTotal']) + '\n' for x in analysisResult]
        text = ''
        # title = [x for x in statisticButtons if statisticButtons.values() == cat_id]
        # print(title)
        for x in analysisText:
            text += x
        # bot.send_message(message.chat.id, title[0].upper() + '\n' + text)
        if len(text) == 0:
            bot.send_message(message.chat.id, 'В это время операции не было')
        else:
            bot.send_message(message.chat.id, text)
        conn.close()
    except:
        text_sad = bot.send_message(message.chat.id, 'Некорректный ввод, попробуйтей снова')
        bot.register_next_step_handler(text_sad, financial_analysis)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    conn = fdbw.FDBWorker()
    if not (conn.user_exist(str(message.chat.id))):
        firstSum = bot.send_message(message.chat.id, 'Введите первоначальную сумму перед регистрацией')
        bot.register_next_step_handler(firstSum, regist)
    else:
        first_keyboard(message)
    conn.close()


@bot.message_handler(content_types=["text"])
def keyboard(message):
    if message.text == 'Главное меню':
        first_keyboard(message)

    if message.text == 'Занесение информации о финансовой операции':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        markup.add(*[types.KeyboardButton(text=x) for x in parentButtons], 'Главное меню')
        bot.send_message(message.chat.id, 'Выберите вид операции', reply_markup=markup)
        # msg = bot.reply_to(message, 'ну поехали', reply_markup=markup)
        # bot.register_next_step_handler(msg, process_step)  # TODO: погуглить это говно и это bot.set_update_listener()

    if message.text in parentButtons:
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add(*[x['Name'] for x in sours if x['Parent'] == message.text], 'Главное меню')
        bot.send_message(message.chat.id, 'Выберите тип операции', reply_markup=markup)
        # bot.register_next_step_handler(info, hyi)

    if message.text in childButtons:
        global type_id
        for x in sours:
            if x['Name'] == message.text:
                type_id = x['@Categories']
                break
        infoText = bot.send_message(message.chat.id, 'введите сумму')
        bot.register_next_step_handler(infoText, operation_send)

    if message.text == 'Проверить состояние счета':
        conn = fdbw.FDBWorker()
        accounts = fdbw.AccountWorker(conn, message.chat.id)
        current_funds = accounts.get_accounts(acc_id='51')[0]['AccountTotal']
        bot.send_message(message.chat.id, "На вашем счете: " + str(current_funds))
        conn.close()

    if message.text == 'Финансовая отчетность':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        markup.add(*[types.KeyboardButton(text=x) for x in statisticButtons], 'Отчет о финансовых результатах',
                   'Главное меню')
        # markup.add(*[x for x in statisticButtons], 'отчет о финансовых результатах') можно писать и так. никакой разницы
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)

    if message.text in statisticButtons.keys():
        global cat_id
        cat_id = statisticButtons[message.text]
        infoText = bot.send_message(message.chat.id, 'Введите 2 даты через запятую, в формате гггг-мм-дд')
        bot.register_next_step_handler(infoText, financial_analysis)

    if message.text == 'Отчет о финансовых результатах':
        conn = fdbw.FDBWorker()
        statistic = fdbw.AssetsWorker(conn, message.chat.id)
        activ = ''
        passiv = ''
        activ_sum = 0
        passiv_sum = 0
        for x in statistic.get_balance():
            if x['Type'] == 1:
                activ += x['Name'] + ': ' + str(x['CurrentTotal']) + '\n'
                activ_sum += x['CurrentTotal']
            else:
                passiv += x['Name'] + ': ' + str(x['CurrentTotal']) + '\n'
                passiv_sum += x['CurrentTotal']
        # statistic = [x['Name'] + ': ' + str(x['CurrentTotal']) + '\n' for x in statistic.get_balance()]
        # text = ''
        # for x in statistic:
        #     text += x
        bot.send_message(message.chat.id,"АКТИВ\n___________________\n" + activ + "___________________\nИтог: " + str(
            activ_sum) + "\n\n" +"ПАССИВ\n___________________\n" + passiv + "___________________\nИтог: " + str(
            passiv_sum) + "\n")
        conn.close()

        # print('asdsad')
        # bot.send_message()
        ##ИНТЕРЕЕЕЕЕЕСНО!
        # mark = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        # a = types.KeyboardButton(text='asdasd',request_location=True)
        # mark.add(a)
        # bot.send_message(chat_id,text='asdas', reply_markup=mark)
        #
        # elif message.text == 'Приобретение материалов и товаров':
        #     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        #     markup.add(*[x for x in buttons.keys() if buttons.values() == message.chat.id])
        # elif message.text == 'Кредиты и другие долги':
        #     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        #     markup.add(*[x for x in buttons.keys() if buttons.values() == message.chat.id])
        # elif message.text == 'Оплаты от дебиторов/покупателей':
        #     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        #     markup.add(*[x for x in buttons.keys() if buttons.values() == message.chat.id])
        #     # f = open('m.ogg', 'rb')
        #     # bot.send_audio(message.chat.id, f, """this place isn't yours anymore""")


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
