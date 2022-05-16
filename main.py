from handlers import *

# the token is given by BotFather bot and hidden in .txt file
with open('token.txt', 'r', encoding='utf-8') as t, open('password.txt', 'r', encoding='utf-8') as p:
    token = t.read().strip()
    password = p.read().strip()
# command: function to call. All these functions are in handlers module
handlers_dict = {
            '/dates': 'set_dates',
            '/start': 'start_handler',
            '/restart': 'start_handler',
            '/book': 'book_handler',
            '/info': 'info_handler',
            '/vacant': 'vacant_handler',
            '/my_suits': 'show_suits_handler',
            '/delete': 'delete_suits_handler'
            }


def message_handler(message: json) -> (int, str, str, int, str, str):
    """
    Works on a data from Telegram server update
    """
    # message is a reply from a button
    if 'callback_query' in message:
        data = message['callback_query']['data']
        for i in range(len(data)):
            if data[i].isspace():
                command = data[:i]
                additional = data[i + 1:]
                break
        else:
            command = data
            additional = None
        chat = message['callback_query']['message']['chat']['id']
        user_id = message['callback_query']['from']['id']
        user_first_name = message['callback_query']['from']['first_name']
        try:
            user_last_name = message['callback_query']['from']['last_name']
        except KeyError:
            user_last_name = 'n/a'
    # message is a forced reply
    elif 'message' in message and 'reply_to_message' in message['message']:
        text = message['message']['text']
        command = '/dates'
        chat = message['message']['chat']['id']
        additional = text if 'окончания' in message['message']['reply_to_message']['text'] else text + ' ' + 'begin'
        user_id = message['message']['from']['id']
        user_first_name = message['message']['from']['first_name']
        try:
            user_last_name = message['message']['from']['last_name']
        except KeyError:
            user_last_name = 'n/a'
    else:
        # just a common message
        command = message['message']['text']
        chat = message['message']['chat']['id']
        additional = None
        user_id = message['message']['from']['id']
        user_first_name = message['message']['from']['first_name']
        try:
            user_last_name = message['message']['from']['last_name']
        except KeyError:
            user_last_name = 'n/a'
    return chat, command, additional, user_id, user_first_name, user_last_name


def wrong_command(chat_id):
    """
    Called when the bot doesn't know the command taken from a user. Sends a message.
    """
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
            "command": "delete",
            "description": "Удалить забронированнные номера"
        },
        {
            "command": "restart",
            "description": "Начать сначала"
        }
    ]}
    data = json.dumps(data_to_set)
    try:
        requests.post(f'https://api.telegram.org/bot{token}/setMyCommands', headers=header, data=data)
    except Exception:
        print("Can't set commands")


def get_updates():
    """
    Basic function with the main endless loop. Gets update from the Telegram server.
    """
    params = {
        'offset': 0,
        'timeout': 2
    }
    while True:
        try:
            response = requests.post(f'https://api.telegram.org/bot{token}/getUpdates', params=params)
        except Exception:
            print("For some reason can't get updates from the Telegram server")
            continue
        updates = response.json()
        if response.status_code != 200 or updates['ok'] == False:
            print("For some reason can't get updates from the Telegram server")
            continue
        if updates['result']:
            for new_message in updates['result']:
                print(new_message)
                try:
                    chat, command, additional_info, *user = message_handler(new_message)
                except KeyError as error:
                    print('There is no such parameter in the message. Info:', error)
                    continue
                if command in handlers_dict:
                    handler_to_call = handlers_dict[command]
                    try:
                        globals()[handler_to_call](chat, command, additional_info, user)
                    except Exception as info:
                        print('Error when a function is running.', info)
                        wrong_command(chat)
                else:
                    wrong_command(chat)
            # marks the last message of the update as seen and handled (in order to not handle them again)
            last_id = updates['result'][-1]['update_id']
            params['offset'] = last_id + 1


if __name__ == '__main__':
    set_commands()
    get_updates()
