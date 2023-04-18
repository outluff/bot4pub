import telebot
import configure
from telebot import types
import re
import sqlite3
import random

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
    reg_button = types.KeyboardButton(text="Share your phone number", request_contact=True)
    markup_reply.add(reg_button)
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, NScardbot приветствует тебя!!\nЧтобы идентифицировать тебя мы, в первую очередь, используем твой чат id.\nыТакже нам требуется твой номер телефонаи дата рождения. Если у тебя нет желания оставлять нам свой номер телефона, то, к сожлению, ты не сможешь со мной общаться. ', reply_markup=markup_reply)

@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
    cur.execute("INSERT INTO phonenumber (")

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'Оператор':
        return send_mes(call.message)


@bot.message_handler(content_types=['text'])
def get_text(message):
    item1 = types.KeyboardButton(text='Код авторизации')
    item2 = types.KeyboardButton(text='Карта лояльности')
    item3 = types.KeyboardButton(text='Розыгрыши')
    item4 = types.KeyboardButton(text='ADMIN')
    item5 = types.KeyboardButton(text='Ваш адрес')
    item6 = types.KeyboardButton(text='Отзывы и предложения')
    item7 = types.KeyboardButton(text='Бронирование')
    item8 = types.KeyboardButton(text='Есть вопрос')
    if message.text == 'Код авторизации':
        return chislo(message)
    elif message.text == 'Ваш адрес':
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
        item5 = types.KeyboardButton(text='Ваш адрес')
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
    #elif message.text == 'Редактировать бронирование':
        #return editbron(message)

    elif message.text == 'Отзывы и предложения':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(text='Новый отзыв/предложение')
        item2 = types.KeyboardButton(text='Показать прошлые')
        back = types.KeyboardButton(text='Меню')
        markup_reply.add(item1, item2, back)
        bot.send_message(message.chat.id, 'Вы хотите написать новый отзыв/предложение или посмотреть и отредактировать старые отызвы/предложения?', reply_markup=markup_reply)
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
    elif message.text == 'Карта лояльности':
        return loyaltycard(message)
    #elif message.text == 'Дата':
        #return dataedit(message)


@bot.message_handler(func=lambda message: True)
def data(message):
    msg = bot.send_message(message.chat.id, 'Напишите дату, на которую хотите забронировать стол(формат: дд/мм): ')
    bot.register_next_step_handler(msg, time)


def time(message):
    data = message.text
    if not is_date_format(data):
        msg = bot.send_message(message.chat.id, 'Пожалуйста, используйте указанный формат')
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
    chel = message.text
    if not chel.isdigit():
        msg = bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(msg, chel)
        return
    c = con.cursor()
    c.execute("INSERT INTO bron ( date, time, chel) VALUES ( ?, ?, ?)", (data, time, chel))
    con.commit()
    bot.send_message(message.chat.id, 'Ваше бронирование: Следующая станция - Сокол, дата: %s , время: %s, количество человек: %s ' % (data, time, chel))


#def editbron(message):
    #user_id = message.chat.id
    #cur.execute("SELECT * FROM bron WHERE user_id = ?", (user_id,))
    #result = cur.fetchone()
    #if result is None:
        #bot.send_message(message.chat.id, 'На ближайшее время у вас нет активного бронирования')
    #else:
        #markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #item1 = types.KeyboardButton(text='Дата')
        #item2 = types.KeyboardButton(text='Время')
        #item3 = types.KeyboardButton(text='Количество гостей')
        #back = types.KeyboardButton(text='Меню')
        #markup_reply.add(item1, item2, item3, back)
        #bot.send_message(message.chat.id, 'Выберите, что вы хотите отредактировать', reply_markup=markup_reply)


#def dataedit(message):
    #cur.execute("SELECT * FROM bron WHERE date = ?", (data,))
    #result = cur.fetchone()
    #bot.send_message(message.chat.id, {result})



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
    sql = "SELECT otziv FROM otzivi ORDER BY id "
    cur.execute(sql)
    result = cur.fetchone()
    bot.send_message(user_id, {result})
    con.commit()


def chislo(message):
    global beg
    global end
    beg = 1
    end = 1600
    random_integer = random.randint(beg, end)
    bot.send_message(message.chat.id, 'Ваш код авторизации: %s' %(random_integer))


def loyaltycard(message):
    user_id = message.chat.id
    cur.execute("SELECT * FROM loyalty_card WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    if result is None:
        cardnum = ''.join([str(random.randint(0, 9)) for i in range(16)])
        cur.execute("INSERT INTO loyalty_card (user_id, cardnum, nakop, giftsbonus, promotebnus, deposit, bonustogift) VALUES (?, ?, 0, 0, 0, 0, 0)", (user_id, cardnum))
        con.commit()
        message_text = f"Номер вашей карты: {cardnum}\n\nВы еще не заработали никаких бонусов."
    else:
        user_id, cardnum, nakop, giftsbonus, promotebnus, deposit, bonustogift = result
        message_text = f"Номер вашей карты: {cardnum}\n\nКоличество бонусов:\nНакопленные бонусы: {nakop} руб.\nПодарочные бонусы: {giftsbonus} руб.\nАкционные бонусы: {promotebnus} руб.\nДепозит: {deposit} руб.\nБонусы доступные для дарения другу: {bonustogift} руб."

    bot.send_message(user_id, message_text)


bot.polling(none_stop=True, interval=0)
