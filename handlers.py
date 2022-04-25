import requests
import json

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'


def start_handler(chat_id):
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


def book_handler(chat_id):
    print('book_handler is on')


def info_handler(chat_id):
    print('info_handler is on')


def vacant_handler(chat_id):
    print('vacant_handler is on')


def suits_handler(chat_id):
    print('suit_handler is on')
