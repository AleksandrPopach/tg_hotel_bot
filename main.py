import requests

token = '5398687279:AAF4t4akIuMjo2Zmrmd2GBX5SGAOg-Ot6as'
params = {
    'offset': 0,
    'timeout': 2
}

while True:
    response = requests.post(f'https://api.telegram.org/bot{token}/getUpdates', params=params)
    updates = response.json()
    if not updates['result']:
        print('No messages')
    else:
        for new_message in updates['result']:
            print(new_message['message']['text'])
        last_id = updates['result'][-1]['update_id']
        params['offset'] = last_id + 1
        if updates['result'][-1]['message']['text'] == 'stop':
            break



