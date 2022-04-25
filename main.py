import requests
import json
from handlers import *

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'
handlers = {
            '/start': 'start_handler',
            '/restart': 'start_handler',
            '/book': 'book_handler',
            '/info': 'info_handler',
            '/vacant': 'vacant_handler',
            '/my_suits': 'suits_handler'
            }


def wrong_command(chat_id):
    header = {'Content-Type': 'application/json'}
    params = {
        'chat_id': chat_id,
        'text': "Такой команды не существует. Для списка доступных команд наберите '/' в строке чата,\
 либо используйте команду /start для запуска главного меню."
    }
    data = json.dumps(params)
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', headers=header, data=data)


def set_commands():
    header = {'Content-Type': 'application/json'}
    data_to_set = {"commands": [
        {
            "command": "book",
            "description": "Забронировать номер"
        },
        {
            "command": "info",
            "description": "Информация об отелях"
        },
        {
            "command": "vacant",
            "description": "Список свободных номеров"
        },
        {
            "command": "my_suits",
            "description": "Мои забронированнные номера"
        },
        {
            "command": "restart",
            "description": "Начать сначала"
        }
    ]}
    data = json.dumps(data_to_set)
    requests.post(f'https://api.telegram.org/bot{token}/setMyCommands', headers=header, data=data)


def get_updates():
    params = {
        'offset': 0,
        'timeout': 2
    }
    while True:
        response = requests.post(f'https://api.telegram.org/bot{token}/getUpdates', params=params)
        updates = response.json()
        if updates['result']:
            for new_message in updates['result']:
                print(new_message)
                if 'callback_query' in new_message:
                    text = new_message['callback_query']['data']
                    chat = new_message['callback_query']['message']['chat']['id']
                elif 'message' in new_message:
                    text = new_message['message']['text']
                    chat = new_message['message']['chat']['id']
            if text in handlers:
                handler_to_call = handlers[text]
                globals()[handler_to_call](chat)
            else:
                wrong_command(chat)
            last_id = updates['result'][-1]['update_id']
            params['offset'] = last_id + 1


set_commands()
get_updates()
