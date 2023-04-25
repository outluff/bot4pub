import telebot
import configure
from telebot import types
import re
import sqlite3
import random
import datetime

con = sqlite3.connect("test.db", check_same_thread=False)
cur = con.cursor()
time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
date_re = re.compile(r'\d\d/\d\d')
dateofbirth_re = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])[/](0?[1-9]|1[0-2])[/](19[4-9]\d|20[01]\d|2020)$')

def is_time_format(s):
    return bool(time_re.match(s))


def is_date_format(s):
    return bool(date_re.match(s))


def is_dateofbirth_format(s):
    return bool(dateofbirth_re.match(s))


bot = telebot.TeleBot(configure.config['token'], skip_pending=True)
adm = 467752313


@bot.message_handler(commands=['start'])
def himes(message):
    markup_reply = types.ReplyKeyboardMarkup()
    reg_button = types.KeyboardButton(text="Share your phone number", request_contact=True)
    markup_reply.add(reg_button)
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, NScardbot приветствует тебя!!\nЧтобы идентифицировать тебя мы, в первую очередь, используем твой чат id.\nТакже нам требуется твой номер телефона и дата рождения. Если у тебя нет желания оставлять нам свой номер телефона, то, к сожалению, ты не сможешь со мной общаться. ', reply_markup=markup_reply)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        user_id = message.chat.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        phone_number = message.contact.phone_number
        msg = bot.send_message(user_id, "Введите вашу дату рождения в формате ДД/ММ/ГГГГ (например, 01/01/1990)")
        bot.register_next_step_handler(msg, process_dob, user_id, phone_number, first_name, last_name)


def process_dob(message, user_id, phone_number, first_name, last_name):
    dateofbirth = message.text
    try:
        dob = datetime.datetime.strptime(dateofbirth, '%d/%m/%Y')
        if dob.year < 1945 or dob.year > 2020 or dob.month < 1 or dob.month > 12 or dob.day < 1 or dob.day > 31:
            raise ValueError()
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Некорректная дата рождения. Пожалуйста, введите дату в формате ДД/ММ/ГГГГ')
        bot.register_next_step_handler(msg, process_dob, user_id, phone_number, first_name, last_name)
        return

    cur.execute("INSERT INTO dostup (user_id, phone_number, first_name, last_name, dateofbirth) VALUES (?, ?, ?, ?, ?)", (user_id, phone_number, first_name, last_name, dateofbirth))
    con.commit()
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
    bot.send_message(message.chat.id, "Спасибо, что вы с нами, теперь выбирайте!", reply_markup=markup_reply)






@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'Оператор':
        return send_mes(call.message)
    elif call.data == 'Участвовать':
        return uchastie(call.message)


def handle_callback_query(call):
    callback_data = call.data
    try:
        if call.message:
            if callback_data.startswith('edit_bron:'):
                booking_id = int(callback_data.split(':')[1])
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, f"Вы выбрали бронирование с id {booking_id}")
                bot.answer_callback_query(callback_query_id=call.id, text="Вы выбрали бронирование")
                bot.register_next_step_handler(call.message, edit_bron_handler, booking_id)
    except Exception as e:
        print(e)


@bot.message_handler(content_types=['text'])
def get_text(message):
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
    elif message.text == 'Редактировать бронирование':
        return editbron(message)

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
            item3  = types.KeyboardButton(text='Выбрать победителя последнего розыгрыша')
            back = types.KeyboardButton(text='Меню')
            markup_reply.add(item1, item2, item3, back)
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
    elif message.text == 'Выбрать победителя последнего розыгрыша':
        return pobeditel(message)


@bot.message_handler(func=lambda message: True)
def add_booking(user_id, date, time, chel):
    cur.execute("INSERT INTO bron (user_id, date, time, chel) VALUES (?, ?, ?, ?)", (user_id, date, time, chel))
    con.commit()
    booking_id = cur.lastrowid
    return booking_id


def data(message):
    if message.text == "Меню":
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
        bot.send_message(message.chat.id, "Вы вышли в меню. Ваше бронирование отменено.", reply_markup=markup_reply)
        return
    user_id = message.chat.id
    msg = bot.send_message(message.chat.id, 'Напишите дату, на которую хотите забронировать стол(формат: дд/мм): ')
    bot.register_next_step_handler(msg, time, user_id)


def time(message, user_id):
    data = message.text
    if not is_date_format(data):
        msg = bot.send_message(message.chat.id, 'Пожалуйста, используйте указанный формат')
        bot.register_next_step_handler(msg, time, user_id)
        return
    msg = bot.send_message(message.chat.id, 'Напишите время, на которое хотите забронировать стол(формат: 17:00): ')
    bot.register_next_step_handler(msg, time_handler, user_id, data)


def time_handler(message, user_id, data):
    if message.text == "Меню":
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
        bot.send_message(message.chat.id, "Вы вышли в меню. Ваше бронирование отменено.", reply_markup=markup_reply)
        return
    time = message.text
    if not is_time_format(time):
        msg = bot.send_message(message.chat.id, 'Используйте формат, пожалуйста ')
        bot.register_next_step_handler(msg, time_handler, user_id, data)
        return
    msg = bot.send_message(message.chat.id, 'Введите количество гостей:')
    bot.register_next_step_handler(msg, chel, user_id, data, time)


def chel(message, user_id, data, time):
    if message.text == "Меню":
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
        bot.send_message(message.chat.id, "Вы вышли в меню. Ваше бронирование отменено.", reply_markup=markup_reply)
        return
    chel = message.text
    if not chel.isdigit():
        msg = bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(msg, chel)
        return
    c = con.cursor()
    c.execute("INSERT INTO bron (user_id, date, time, chel) VALUES (?, ?, ?, ?)", (user_id, data, time, chel))
    con.commit()
    bot.send_message(message.chat.id, 'Ваше бронирование: Следующая станция - Сокол, дата: %s , время: %s, количество человек: %s ' % (data, time, chel))

@bot.callback_query_handler(func=lambda call: True)
def process_callback_edit_bron(call):
    booking_id = int(call.data.split(':')[1])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"Вы выбрали бронирование с id {booking_id}")
    bot.answer_callback_query(callback_query_id=call.id, text="Вы выбрали бронирование")
    bot.register_next_step_handler(call.message, edit_bron_handler, booking_id)

@bot.inline_handler(lambda query: True)
def editbron(message):
    user_id = message.chat.id
    cur.execute("SELECT * FROM bron WHERE user_id = ?", (user_id,))
    results = cur.fetchall()
    if not results:
        bot.send_message(message.chat.id, "У вас нет бронирований")
    else:
        if len(results) == 1:
            booking_id, user_id, date, time, chel = results[0]
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton(text="Дата")
            item2 = types.KeyboardButton(text="Время")
            item3 = types.KeyboardButton(text="Количество гостей")
            item4 = types.KeyboardButton(text="Отменить бронирование")
            item5 = types.KeyboardButton(text="Меню")
            markup.row(item1, item2)
            markup.row(item3, item4)
            markup.add(item5)
            bot.send_message(message.chat.id, f"Ваше бронирование: \nДата: {date} \nВремя: {time} \nКоличество гостей: {chel}",
                             reply_markup=markup)
            bot.register_next_step_handler(message, edit_bron_handler, booking_id)
        else:
            markup = types.InlineKeyboardMarkup()
            for row in results:
                booking_id, user_id, date, time, chel = row
                markup.add(types.InlineKeyboardButton(text=f"{date} {time}", callback_data=f"edit_bron:{booking_id}"))
            bot.send_message(message.chat.id, "У вас несколько бронирований, выберите, какое вы хотите отредактировать:", reply_markup=markup)


def edit_bron_handler(message, bron_id):
    user_input = message.text
    if user_input == "Дата":
        bot.send_message(message.chat.id, "Введите новую дату в формате ДД/ММ")
        bot.register_next_step_handler(message, update_bron_date, bron_id)
    elif user_input == "Время":
        bot.send_message(message.chat.id, "Введите новое время в формате ЧЧ:ММ")
        bot.register_next_step_handler(message, update_bron_time, bron_id)
    elif user_input == "Количество гостей":
        bot.send_message(message.chat.id, "Введите новое количество гостей")
        bot.register_next_step_handler(message, update_bron_guests, bron_id)
    elif user_input == "Отменить бронирование":
        cur.execute("DELETE FROM bron WHERE booking_id=?", (bron_id,))
        con.commit()
        bot.send_message(message.chat.id, "Бронирование отменено")
    else:
        bot.send_message(message.chat.id, "Выберите пункт меню")
        bot.register_next_step_handler(message, edit_bron_handler, bron_id)


def update_bron_date(message, booking_id):
    new_date = message.text
    cur.execute("UPDATE bron SET date=? WHERE booking_id=?", (new_date, booking_id))
    con.commit()
    bot.send_message(message.chat.id, "Дата успешно изменена")
    bot.register_next_step_handler(message, edit_bron_handler, booking_id)


def update_bron_time(message, booking_id):
    time = message.text
    if not re.match(r'\d{2}:\d{2}', time):
        bot.send_message(message.chat.id, "Неверный формат времени. Введите время в формате ЧЧ:ММ")
        bot.register_next_step_handler(message, update_bron_time, booking_id)
    else:
        cur.execute("UPDATE bron SET time=? WHERE booking_id=?", (time, booking_id))
        con.commit()
        bot.send_message(message.chat.id, "Время бронирования обновлено!")
        bot.register_next_step_handler(message, edit_bron_handler, booking_id)



def update_bron_guests(message, booking_id):
    chel = message.text
    if not chel.isdigit():
        bot.send_message(message.chat.id, "Количество гостей должно быть числом. Введите количество гостей еще раз.")
        bot.register_next_step_handler(message, update_bron_guests, booking_id)
    else:
        cur.execute("UPDATE bron SET chel=? WHERE booking_id=?", (chel, booking_id))
        con.commit()
        bot.send_message(message.chat.id, "Количество гостей в бронировании обновлено!")
        bot.register_next_step_handler(message, edit_bron_handler, booking_id)



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
    global user_id
    user_id = message.chat.id
    bot.send_message(adm, str(message.text))
    sql = "INSERT INTO otzivi (user_id, otziv) VALUES (?, ?);"
    cur.execute(sql, (user_id, str(message.text)))
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
    con.commit()
    markup_inline = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Участвовать',  callback_data='Участвовать')
    markup_inline.add(item1)
    bot.send_message(user_id, {result}, reply_markup=markup_inline)


def uchastie(message):
    user_id = message.chat.id
    cur.execute("SELECT text FROM rosigrishi ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    cur.execute("INSERT INTO uchastie (user_id, text) VALUES (?, ?)", (user_id,  result[0].encode('utf-8')))
    con.commit()
    bot.send_message(message.chat.id, 'Вы занесены в базу участников этого розыгрыша!')


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
    sql = "SELECT otziv FROM otzivi WHERE user_id = ?"
    cur.execute(sql, (user_id,))
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


def pobeditel(message):
    cur.execute("""
        SELECT COUNT(*) as total_participants FROM uchastie
        WHERE text = (
            SELECT text FROM rosigrishi ORDER BY id DESC LIMIT 1
        )
    """)
    result = cur.fetchone()
    bot.send_message(message.chat.id, f"Общее количество участников последнего розыгрыша: {result[0]}")

    cur.execute("""
        SELECT * FROM uchastie
        WHERE text = (
            SELECT text FROM rosigrishi ORDER BY id DESC LIMIT 1
        ) ORDER BY RANDOM() LIMIT 1
    """)
    result = cur.fetchone()
    bot.send_message(message.chat.id, f"Победитель: {result}")


bot.polling(none_stop=True, interval=0)
