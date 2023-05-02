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
        return book_table(message)

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


def book_table(message):
    user_id = message.chat.id
    # Проверка количества бронирований пользователя в БД
    num_bookings = get_user_bookings_count(user_id)
    if num_bookings == 0:
        # Пользователь не имеет ни одного бронирования
        bot.send_message(message.chat.id, "У вас нет текущих бронирований.")
        return data(message)
    elif num_bookings == 1:
        bron_id = get_user_booking_id(user_id)
        show_booking_info(message.chat.id, bron_id)
        msg = bot.send_message(message.chat.id, "Выберите что вы хотите отредактировать")
        bot.register_next_step_handler(msg, edit_bron_handler)
    else:
        keyboard = create_booking_keyboard(user_id)  # Создаем клавиатуру с выбором бронирования
        bot.send_message(message.chat.id, "Выберите бронирование для редактирования:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_booking:'))
def edit_booking(call):
    bron_id = call.data.split(':')[1]  # Получаем идентификатор выбранного бронирования
    show_booking_info(call.message.chat.id, bron_id)  # Отображаем информацию о бронировании
    msg = bot.send_message(call.message.chat.id, "Выберите что вы хотите отредактировать")
    bot.register_next_step_handler(msg, edit_bron_handler)


def get_user_bookings_count(user_id):
    cur.execute("SELECT COUNT(*) FROM bron WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    return count


def get_user_booking_id(user_id):
    cur.execute("SELECT id FROM bron WHERE user_id = ?", (user_id,))
    bron_id = cur.fetchone()
    if bron_id:
        return bron_id[0]
    return None


def show_booking_info(chat_id, bron_id):
    cur.execute("SELECT * FROM bron WHERE id = ?", (bron_id,))
    booking_info = cur.fetchone()
    if booking_info:
        date = booking_info[2]
        time = booking_info[3]
        chel = booking_info[4]
        bot.send_message(chat_id, f"Информация о бронировании {bron_id}:\nДата: {date}\nВремя: {time} \nКоличество гостей: {chel}")
    else:
        bot.send_message(chat_id, "Бронирование не найдено")
    msg = bot.send_message(chat_id, "Продолжаем")
    bot.register_next_step_handler(msg, edit_bron_handler)


def create_booking_keyboard(user_id):
    keyboard = types.InlineKeyboardMarkup()
    bookings = get_user_bookings(user_id)
    for booking in bookings:
        bron_id = booking[0]
        date = booking[2]
        time = booking[3]
        chel = booking[4]
        booking_info = f"Дата: {date} Время: {time} Количество гостей: {chel}"
        callback_data = f"edit_booking:{bron_id}"
        keyboard.add(types.InlineKeyboardButton(text=booking_info, callback_data=callback_data))
    return keyboard

def get_user_bookings(user_id):
    cur.execute("SELECT * FROM bron WHERE user_id = ?", (user_id,))
    bookings = cur.fetchall()
    return bookings


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
    sql = "INSERT INTO rosigrishi (text_ros) VALUES (?);"
    cur.execute(sql, (str(message.text),))
    con.commit()


def dlya_usera(message):
    print('dlya_usera')
    print(message.chat.id)
    global user_id
    user_id = message.chat.id
    sql = "SELECT text_ros FROM rosigrishi ORDER BY id DESC LIMIT 1"
    cur.execute(sql)
    result = cur.fetchone()
    markup_inline = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Участвовать',  callback_data='Участвовать')
    markup_inline.add(item1)
    bot.send_message(user_id, {result}, reply_markup=markup_inline)
    con.commit()


def uchastie(message):
    user_id = message.chat.id
    cur.execute("SELECT text_ros FROM rosigrishi ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    cur.execute("INSERT INTO uchastie (user_id, text_uch) VALUES (?, ?)", (user_id,  result[0]))
    con.commit()
    bot.send_message(message.chat.id, 'Вы занесены в базу участников этого розыгрыша!')


def spisokprosh(message):
    print('dlya_usera')
    print(message.chat.id)
    cur.execute('SELECT text_ros FROM rosigrishi ORDER BY id')
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
    cur.execute("SELECT text_ros FROM rosigrishi ORDER BY id DESC LIMIT 1")
    last_draw = cur.fetchone()[0]

    # Получение количества участников последнего розыгрыша
    cur.execute("SELECT COUNT(*) FROM uchastie WHERE text_uch = ?", (last_draw,))
    total_participants = cur.fetchone()[0]

    # Выбор случайного победителя
    cur.execute("SELECT user_id, text_uch FROM uchastie WHERE text_uch = ?", (last_draw,))
    participants = cur.fetchall()
    random_winner = random.choice(participants)

    # Вывод информации на экран админа
    response = f"Общее количество участников последнего розыгрыша: {total_participants}\n"
    response += f"Случайный победитель:\nИдентификатор пользователя: {random_winner[0]}\nТекст розыгрыша: {random_winner[1]}"
    bot.send_message(message.chat.id, response)


bot.polling(none_stop=True, interval=0)
