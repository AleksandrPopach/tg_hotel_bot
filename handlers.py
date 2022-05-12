import requests
import json
import psycopg2
import re
import datetime

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'


def incorrect_data(chat_id):
    """
    Called when the data sent by the user is invalid. Sends a message.
    """
    header = {'Content-Type': 'application/json'}
    params = {
        'chat_id': chat_id,
        'text': "Вы ввели некорректные данные! Внимательно читайте указания и попробуйте снова."
    }
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def correct_db(user_id: int):
    """
    Deletes from db all incomplete bookings made by the user. Corrects the amount of vacant suits.
    """
    con = psycopg2.connect(
        database="hotels",
        user="bra1n",
        password="050888",
        host="localhost",
        port="5432"
    )
    cur = con.cursor()
    cur.execute(f"DELETE FROM book WHERE id IN (SELECT id FROM book \
    WHERE client_id = {user_id} AND (arrival_date IS NULL or departure_date IS NULL))")
    cur.execute(f"UPDATE hotel_suit SET vacant_amount = vacant_amount - 1 WHERE \
    hotel_id = (SELECT hotel_id FROM book WHERE client_id = {user_id} ORDER BY id DESC LIMIT 1) AND \
    suit_id = (SELECT suit_id FROM book WHERE client_id = {user_id} ORDER BY id DESC LIMIT 1)")
    cur.close()
    con.commit()
    con.close()


def set_dates(chat_id, command, additional_info, user):
    def is_valid_date(date_to_check: str):
        pattern = r'\d\d-\d\d-\d\d\d\d'
        check = re.match(pattern, date_to_check)
        if not check:
            return False
        day, month, year = list(map(int, date_to_check.split('-')))
        try:
            datetime.date(year, month, day)
        except ValueError:
            return False
        else:
            return True

    if 'begin' in additional_info:
        date_to_add = additional_info[:-6].strip()
        column = 'arrival_date'
        text = 'Введите желаемую дату окончания заезда в формате ДД-ММ-ГГГГ. Например, 01-12-2000 (1 декабря 2000 г.)'
        params = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': {
                'force_reply': True,
                'input_field_placeholder': 'ДД-ММ-ГГГГ'
            }
        }
    else:
        date_to_add = additional_info.strip()
        column = 'departure_date'
        params = {
            'chat_id': chat_id,
            'text': 'Вы успешно забронировали номер. Просмотреть свои действующие брони можно с помощью команды\
             /my_suits, а удалить их с помощью /delete. Также все действия доступны из главного меню.'
        }
    if not is_valid_date(date_to_add):
        incorrect_data(chat_id)
        return

    con = psycopg2.connect(
        database="hotels",
        user="bra1n",
        password="050888",
        host="localhost",
        port="5432"
    )
    cur = con.cursor()
    cur.execute(f"UPDATE book SET {column} = '{date_to_add}' WHERE id = \
    (SELECT id FROM book WHERE client_id = '{user[0]}' ORDER BY id DESC LIMIT 1)")
    cur.close()
    con.commit()
    con.close()

    if column == 'departure_date':
        correct_db(user[0])
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def pull_data_from_db(query: str) -> list:
    """
    Sets connection to PostgreSQL database and returns data by a list of tuples.
    """
    con = psycopg2.connect(
        database="hotels",
        user="bra1n",
        password="050888",
        host="localhost",
        port="5432"
    )
    cur = con.cursor()
    cur.execute(query)
    items = cur.fetchall()
    cur.close()
    con.close()
    return items


def send_list_of_hotels_or_suits(chat_id, command, hotel=None):
    if hotel:
        # if the hotel is defined by the user, then we show which suits are available at the moment
        items = pull_data_from_db(f"SELECT suit.name FROM suit JOIN hotel_suit ON suit.id = hotel_suit.suit_id \
        JOIN hotel ON hotel.id = hotel_suit.hotel_id WHERE hotel.name = '{hotel}' AND vacant_amount != 0 \
        ORDER BY hotel.id, suit.id;")
    else:
        items = pull_data_from_db('SELECT name FROM hotel;')
    names = [c[0] for c in items]
    # form inline keyboard
    keyboard = []
    for i in range(len(names)):
        button = []
        button_content = dict()
        button_content["text"] = names[i]
        button_content["callback_data"] = command + " " + names[i]
        if hotel:
            button_content["callback_data"] = button_content["callback_data"] + " " + hotel
        button.append(button_content)
        keyboard.append(button)
    text = 'Выберите номер:' if hotel else 'Выберите отель:'
    params = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {
            "inline_keyboard": keyboard
        }
    }
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def send_photo(chat_id, url):
    params = {
        'photo': url,
        'chat_id': chat_id
    }
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendPhoto', headers=header, data=data)


def start_handler(chat_id, *args):
    header = {'Content-Type': 'application/json'}
    params = {
        'chat_id': chat_id,
        'text': 'Здравствуйте. Выберите действие:',
        'reply_markup': {
                         "inline_keyboard": [[{"text": "Забронировать номер", "callback_data": "/book"}],
                                             [{"text": "Информация об отелях", "callback_data": "/info"}],
                                             [{"text": "Список свободных номеров", "callback_data": "/vacant"}],
                                             [{"text": "Мои забронированнные номера", "callback_data": "/my_suits"}],
                                             [{"text": "Удалить забронированнные номера", "callback_data": "/delete"}],
                                             [{"text": "В главное меню", "callback_data": "/restart"}]
                                             ]}
            }
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def book_handler(chat_id, command, name, user: list):
    """
    Allow the user to book a suit. Sets connection to the db and add data to it.
    :param chat_id: id of the chat for the answer
    :param command: /book
    :param name: If not None, it can be either the name of a hotel or a composite string 'suit + hotel'.
    :param user: list of the user's id and full name.
    """
    user = tuple(user)
    if name:
        con = psycopg2.connect(
            database="hotels",
            user="bra1n",
            password="050888",
            host="localhost",
            port="5432"
        )
        cur = con.cursor()
        cur.execute('SELECT name FROM hotel')
        hotels = cur.fetchall()
        cur.close()
        for hotel in hotels:
            if name == hotel[0]:
                cur2 = con.cursor()
                cur2.execute('SELECT id FROM client;')
                client_ids = [c[0] for c in cur2.fetchall()]
                if user[0] not in client_ids:
                    sql = "INSERT INTO client (id, first_name, last_name) VALUES (%s, %s, %s);"
                    cur2.execute(sql, user)
                cur2.close()
                con.commit()
                con.close()
                send_list_of_hotels_or_suits(chat_id, command, name)
                break
        else:
            # name == 'suit + " " + hotel'
            for i in range(len(name)):
                if name[i].isspace():
                    suit = name[:i]
                    hotel = name[i + 1:]
                    break
            else:
                # never get here, just for a good measure
                suit = hotel = 'Неизвестно'

            user_id = user[0]
            cur2 = con.cursor()
            cur2.execute(f"SELECT id FROM hotel WHERE name = '{hotel}';")
            hotel_id = cur2.fetchone()[0]
            cur2.execute(f"SELECT id FROM suit WHERE name = '{suit}';")
            suit_id = cur2.fetchone()[0]
            sql = 'INSERT INTO book (client_id, hotel_id, suit_id) VALUES (%s, %s, %s);'
            cur2.execute(sql, (user_id, hotel_id, suit_id))
            cur2.close()
            con.commit()
            con.close()

            params = {
                'chat_id': chat_id,
                'text': 'Введите желаемую дату заезда в формате ДД-ММ-ГГГГ. Например, 01-12-2000 (1 декабря 2000 г.)',
                'reply_markup': {
                    'force_reply': True,
                    'input_field_placeholder': 'ДД-ММ-ГГГГ'
                }
            }
            header = {'Content-Type': 'application/json'}
            data = json.dumps(params)
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)
    else:
        # name == None
        send_list_of_hotels_or_suits(chat_id, command)


def info_handler(chat_id, command, name, *args):
    if name:
        hotels = pull_data_from_db('SELECT name, address, stars, photo FROM hotel;')
        for hotel in hotels:
            if name == hotel[0]:
                address = hotel[1]
                stars = hotel[2]
                photo = hotel[3]

                send_photo(chat_id, photo)

                params = {
                    'chat_id': chat_id,
                    'text': f'Название отеля: {name},\nАдрес отеля: {address},\nКоличество звёзд: {stars}.'
                }
                break
        else:
            params = {
                'chat_id': chat_id,
                'text': 'Такого отеля нет в базе'
            }
        header = {'Content-Type': 'application/json'}
        data = json.dumps(params)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)
    else:
        send_list_of_hotels_or_suits(chat_id, command)


def vacant_handler(chat_id, command, name, *args):
    if name:
        rows = pull_data_from_db('SELECT hotel.name, suit.name, overall_amount, vacant_amount FROM \
        hotel JOIN hotel_suit ON hotel.id = hotel_suit.hotel_id JOIN suit ON suit.id = hotel_suit.suit_id;')
        suits = dict()
        for row in rows:
            if row[0] in suits:
                suits[row[0]].append(row[1:])
            else:
                suits[row[0]] = [row[1:]]
        information = suits[name]
        text = f'Название отеля: {name}\n\n'
        for suit in information:
            text_to_add = f'Номер: {suit[0]}\nВсего: {suit[1]}\nСвободных: {suit[2]}\n\n'
            text += text_to_add
        params = {
            'chat_id': chat_id,
            'text': text
        }
        header = {'Content-Type': 'application/json'}
        data = json.dumps(params)
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)
    else:
        send_list_of_hotels_or_suits(chat_id, command)


def show_suits_handler(chat_id, command, additional, user):
    sql = f"SELECT hotel.name, suit.name, arrival_date, departure_date \
    FROM hotel JOIN book ON hotel.id = book.hotel_id \
    JOIN suit ON suit.id = book.suit_id WHERE client_id = {user[0]};"
    bookings = pull_data_from_db(sql)
    text = 'Ваши забронированные номера:\n\n'
    for booking in bookings:
        hotel = booking[0]
        suit = booking[1]
        arrival_date = f'{booking[2].day}.{booking[2].month}.{booking[2].year}'
        departure_date = f'{booking[3].day}.{booking[3].month}.{booking[3].year}'
        text_to_add = f'Отель: {hotel}\nНомер: {suit}\nДата заезда: {arrival_date}\nДата отъезда: {departure_date}\n\n'
        text += text_to_add
    params = {
        'chat_id': chat_id,
        'text': text
    }
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def delete_suits_handler(chat_id, command, book_id, user):
    if book_id:
        # id of the booking that should be deleted is defined by the user
        con = psycopg2.connect(
            database="hotels",
            user="bra1n",
            password="050888",
            host="localhost",
            port="5432"
        )
        cur = con.cursor()
        cur.execute(f'SELECT hotel_id, suit_id from book WHERE id = {book_id}')
        hotel_id, suit_id = cur.fetchone()
        cur.execute(f'DELETE FROM book WHERE id = {book_id}')
        cur.execute(f'UPDATE hotel_suit SET vacant_amount = vacant_amount + 1 \
        WHERE hotel_id = {hotel_id} AND suit_id = {suit_id}')
        cur.close()
        con.commit()
        con.close()
        params = {
            'chat_id': chat_id,
            'text': 'Запись удалена.'
        }
    else:
        # send a keyboard to determine which booking is to delete
        sql = f"SELECT book.id, hotel.name, arrival_date, departure_date \
            FROM hotel JOIN book ON hotel.id = book.hotel_id \
            JOIN suit ON suit.id = book.suit_id WHERE client_id = {user[0]};"
        bookings = pull_data_from_db(sql)
        # form an inline keyboard
        keyboard = []
        for i in range(len(bookings)):
            button = []
            button_content = dict()
            arrival = bookings[i][2]
            departure = bookings[i][3]
            dates = f'{arrival.day}.{arrival.month}.{arrival.year} - {departure.day}.{departure.month}.{departure.year}'
            button_content["text"] = bookings[i][1] + "   " + dates
            button_content["callback_data"] = command + " " + str(bookings[i][0])
            button.append(button_content)
            keyboard.append(button)
        text = 'Какую бронь хотите удалить?'
        params = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': {
                "inline_keyboard": keyboard
            }
        }
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)
