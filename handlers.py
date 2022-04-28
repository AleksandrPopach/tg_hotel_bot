import requests
import json
import psycopg2

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'


def send_photo(chat_id, url):
    params = {
        'photo': url,
        'chat_id': chat_id
    }
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendPhoto', headers=header, data=data)


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


def start_handler(chat_id, additional):
    header = {'Content-Type': 'application/json'}
    params = {
        'chat_id': chat_id,
        'text': 'Здравствуйте. Выберите действие:',
        'reply_markup': {
                         "inline_keyboard": [[{"text": "Забронировать номер", "callback_data": "/book"}],
                                             [{"text": "Информация об отелях", "callback_data": "/info"}],
                                             [{"text": "Список свободных номеров", "callback_data": "/vacant"}],
                                             [{"text": "Мои забронированнные номера", "callback_data": "/my_suits"}],
                                             [{"text": "В главное меню", "callback_data": "/restart"}]
                                             ]}
            }
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def book_handler(chat_id, name):
    print('book_handler is on')


def info_handler(chat_id, name):
    hotels = pull_data_from_db('SELECT name, address, stars, photo FROM hotel;')
    if name:
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
    else:
        hotel_names = [c[0] for c in hotels]
        keyboard = []
        for i in range(len(hotel_names)):
            button = []
            button_content = dict()
            button_content["text"] = hotel_names[i]
            button_content["callback_data"] = "/info" + " " + hotel_names[i]
            button.append(button_content)
            keyboard.append(button)
        params = {
            'chat_id': chat_id,
            'text': 'Выберите отель:',
            'reply_markup': {
                "inline_keyboard": keyboard
            }
        }
    header = {'Content-Type': 'application/json'}
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def vacant_handler(chat_id, name):
    print('vacant_handler is on')


def suits_handler(chat_id, user):
    print('suit_handler is on')
