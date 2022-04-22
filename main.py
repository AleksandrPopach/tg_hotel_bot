import requests

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'
handlers = {'/start': 'start_handler', '/restart': 'start_handler'}


def start_handler():
    pass


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
                text = new_message['message']['text']
                if text in handlers:
                    handler_to_call = handlers[text]
                    globals()[handler_to_call]()
                else:
                    print('Выдаём список доступных команд пользователю')
            last_id = updates['result'][-1]['update_id']
            params['offset'] = last_id + 1

get_updates()



