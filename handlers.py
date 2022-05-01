import requests
import json
import psycopg2

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'


def personal_data_handler(chat_id, user):
    print(user)


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
    hotels = cur.fetchall()
    cur.close()
    con.close()
    return hotels


def send_list_of_hotels_or_suits(chat_id, command, is_suit=False):
    if is_suit:
        items = pull_data_from_db('SELECT name FROM suit;')
    else:
        items = pull_data_from_db('SELECT name FROM hotel;')
    names = [c[0] for c in items]
    keyboard = []
    for i in range(len(names)):
        button = []
        button_content = dict()
        button_content["text"] = names[i]
        button_content["callback_data"] = command + " " + names[i]
        button.append(button_content)
        keyboard.append(button)
    text = 'Выберите номер:' if is_suit else 'Выберите отель:'
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


def book_handler(chat_id, command, name, user):
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
        for hotel in hotels:
            if name == hotel[0]:
                send_list_of_hotels_or_suits(chat_id, command, True)
                cur.close()
                con.close()
                break
        else:
            params = {
                'chat_id': chat_id,
                'text': f'Вы успешно забронировали {name} номер!'
            }
            header = {'Content-Type': 'application/json'}
            data = json.dumps(params)
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)
    else:
        personal_data_handler(chat_id, user)
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


def show_suits_handler(*args):
    print('show_suit_handler is on')


def delete_suits_handler(*args):
    print('delete_suit_handler is on')
