import telebot
import configure
from telebot import types
import re
import sqlite3

con = sqlite3.connect("test.db", check_same_thread=False)
cur = con.cursor()
time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
date_re = re.compile(r'\d\d/\d\d')


def is_time_format(s):
    return bool(time_re.match(s))


def is_date_format(s):
    return bool(date_re.match(s))


bot = telebot.TeleBot(configure.config['token'], skip_pending=True)
adm = 467752313


@bot.message_handler(commands=['start'])
def himes(message):
    markup_reply = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton(text='Код авторизации')
    item2 = types.KeyboardButton(text='Карта лояльности')
    item3 = types.KeyboardButton(text='Розыгрыши')
    item4 = types.KeyboardButton(text='ADMIN')
    item5 = types.KeyboardButton(text='Где вы находитесь?')
    item6 = types.KeyboardButton(text='Отзывы и предложения')
    item7 = types.KeyboardButton(text='Бронирование')
    item8 = types.KeyboardButton(text='Есть вопрос')

    markup_reply.add(item1, item2, item3, item4, item5, item6, item7, item8)
    bot.send_message(message.chat.id, 'NScardbot приветствует тебя!!', reply_markup=markup_reply)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'Оператор':
        return send_mes(call.message)


@bot.message_handler(content_types=['text'])
def get_text(message):
    # if message.text == 'Код авторизации':
    # bot.send_message(message.chat.id, 'Ваш код авторизации: ', randint(0, 1500))
    if message.text == 'Где вы находитесь?':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('На карте')
        back = types.KeyboardButton('Меню')
        markup_reply.add(item1, back)
        bot.send_message(message.chat.id, "г. Москва, Улица Балтийская, дом 3", reply_markup=markup_reply)
    elif message.text == 'На карте':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton('Меню')
        markup_reply.add(back)
        bot.send_location(message.chat.id, 55.807304, 37.511418, reply_markup=markup_reply)
    elif message.text == 'Есть вопрос':
        markup_inline = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton('Insta', url='https://instagram.com/nextstationsokol?igshid=YmMyMTA2M2Y=')
        item2 = types.InlineKeyboardButton('VK', url='https://vk.com/nextstationsokol')
        item3 = types.InlineKeyboardButton('Facebook', url='https://www.facebook.com/nextstationsokol?mibextid=ZbWKwL')
        item4 = types.InlineKeyboardButton('Оператор', callback_data='Оператор')
        markup_inline.add(item1, item2, item3, item4)
        bot.send_message(message.chat.id, 'Свяжитесь с нами по номеру: 8 (925) 828-38-78, в одной из наших соцсетей или обратитесь к оператору: ', reply_markup=markup_inline)
    elif message.text == 'Меню':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(text='Код авторизации')
        item2 = types.KeyboardButton(text='Карта лояльности')
        item3 = types.KeyboardButton(text='Розыгрыши')
        item4 = types.KeyboardButton(text='ADMIN')
        item5 = types.KeyboardButton(text='Где вы находитесь?')
        item6 = types.KeyboardButton(text='Отзывы и предложения')
        item7 = types.KeyboardButton(text='Бронирование')
        item8 = types.KeyboardButton(text='Есть вопрос')
        markup_reply.add(item1, item2, item3, item4, item5, item6, item7, item8)
        bot.send_message(message.chat.id, 'Выбирайте что вы хотите посмотреть', reply_markup=markup_reply)
    elif message.text == 'Бронирование':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(text='Новая бронь')
        item2 = types.KeyboardButton(text='Редактировать бронирование')
        back = types.KeyboardButton(text='Меню')
        markup_reply.add(item1, item2, back)
        bot.send_message(message.chat.id, 'Выбирай', reply_markup=markup_reply)
    elif message.text == 'Новая бронь':
        return data(message)
    elif message.text == 'Отзывы и предложения':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(text='Новый отзыв/предложение')
        item2 = types.KeyboardButton(text='Показать прошлые')
        back = types.KeyboardButton(text='Меню')
        markup_reply.add(item1, item2, back)
        bot.send_message(message.chat.id, 'Вы хотите написать новый отзыв/предложение или посмотреть и отредактировать старые отызвы/предложения?',
                         reply_markup=markup_reply)
    elif message.text == 'Новый отзыв/предложение':
        return new_otzivi(message)
    elif message.text == 'Показать прошлые':
        return lastotzivi(message)
    elif message.text == 'ADMIN':
        global user_id
        user_id = message.chat.id
        if message.chat.id == 467752313:
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton(text='Добавить новый розыгрыш')
            item2 = types.KeyboardButton(text='Список прошлых розыгрышей')
            back = types.KeyboardButton(text='Меню')
            markup_reply.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Гуд ебининг', reply_markup=markup_reply)
        else:
            bot.send_message(message.chat.id, 'У вас нет доступа')
    elif message.text == 'Добавить новый розыгрыш':
        return rozigrish(message)
    elif message.text == 'Список прошлых розыгрышей':
        return spisokprosh(message)
    elif message.text == 'Розыгрыши':
        return dlya_usera(message)


@bot.message_handler(func=lambda message: True)
def insert_booking(data, time, chel):
    cur.execute("INSERT INTO bron' (date, time, chel) VALUES (%s, %s, %s )", (data, time, chel))
    con.commit()


def data(message):
    msg = bot.send_message(message.chat.id, 'Напишите дату, на которую хотите забронировать стол(формат: дд/мм): ')
    bot.register_next_step_handler(msg, time)


def time(message):
    data = message.text
    if not is_date_format(data):
        msg = bot.send_message(message.chat.id, 'Введите в формате ....')
        bot.register_next_step_handler(msg, time)
        return
    msg = bot.send_message(message.chat.id, 'Напишите время, на которое хотите забронировать стол(формат: 17:00): ')
    bot.register_next_step_handler(msg, time_handler, data)


def time_handler(message, data):
    time = message.text
    if not is_time_format(time):
        msg = bot.send_message(message.chat.id, 'Используйте формат, пожалуйста ')
        bot.register_next_step_handler(msg, time_handler, data)
        return
    msg = bot.send_message(message.chat.id, 'Введите количество гостей:')
    bot.register_next_step_handler(msg, chel, data, time)


def chel(message, data, time):
    try:
        chel = message.text
        if not chel.isdigit():
            msg = bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
            bot.register_next_step_handler(msg, chel)
            return
        #insert_booking(data, time, int(chel))
        bot.send_message(message.chat.id, 'Ваше бронирование: Следующая станция - Сокол, дата: %s , время: %s, количество человек: %s ' % (data, time, chel))
    except Exception as e:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')


def send_mes(message):
    msg = bot.send_message(message.chat.id, 'Задавай свой вопрос')
    bot.register_next_step_handler(msg, forward_adm)


def forward_adm(message):
    print('forward_adm')
    print(message.chat.id)
    bot.send_message(adm, '{}'.format(message.text))
    forward_usr(message)


def forward_usr(message):
    print('forward_usr')
    print(message.chat.id)
    global user_id
    user_id = message.chat.id

    msg = bot.send_message(adm, 'Введи ответ на вопрос')
    bot.register_next_step_handler(msg, forward_usr_1)


def forward_usr_1(message):
    print('forward_usr_1')
    print(message.chat.id)
    bot.send_message(user_id, '{}'.format(message.text))


def new_otzivi(message):
    msg = bot.send_message(message.chat.id, 'Напиши нам и мы прислушаемся')
    bot.register_next_step_handler(msg, for_admin)


def for_admin(message):
    print('for_admin')
    print(message.chat.id)
    bot.send_message(adm, str(message.text))
    sql = "INSERT INTO otzivi (otziv) VALUES (?);"
    cur.execute(sql, (str(message.text),))
    con.commit()

def rozigrish(message):
    msg = bot.send_message(message.chat.id, 'Введите новый розыгрыш')
    bot.register_next_step_handler(msg, dlya_admina)


def dlya_admina(message):
    print('dlya_admina')
    print(message.chat.id)
    bot.send_message(adm, str(message.text))
    sql = "INSERT INTO rosigrishi (text) VALUES (?);"
    cur.execute(sql, (str(message.text),))
    con.commit()


def dlya_usera(message):
    print('dlya_usera')
    print(message.chat.id)
    global user_id
    user_id = message.chat.id
    sql = "SELECT text FROM rosigrishi ORDER BY id DESC LIMIT 1"
    cur.execute(sql)
    result = cur.fetchone()
    bot.send_message(user_id, {result})
    con.commit()

def spisokprosh(message):
    print('dlya_usera')
    print(message.chat.id)
    cur.execute('SELECT text FROM rosigrishi ORDER BY id')
    for row in cur:
        bot.send_message(message.chat.id, row)


def lastotzivi(message):
    print('lastotzivi')
    print(message.chat.id)
    global user_id
    user_id = message.chat.id
    sql = "SELECT otziv FROM otzivi ORDER BY id DESC LIMIT 1"
    cur.execute(sql)
    result = cur.fetchone()
    bot.send_message(user_id, {result})
    con.commit()


bot.polling(none_stop=True, interval=0)
