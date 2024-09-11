

import requests

def send_poll(options,  to_number, caption = 'Escolha uma opção:',):

    url = "https://gate.whapi.cloud/messages/poll"

    payload = {
        "to": to_number,
        "options": options, 
        "title": caption,
        "count": 1,
        "view_once": True
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer IggSqEFstZ8K4E7Pt1XMQFGx5bn3a4L5"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    return response

