# https://medium.com/@whapicloud/python-bot-whatsapp-a-step-by-step-guide-for-developer-b11d600ad7f5

import requests

# URL da API do Whapi.Cloud para enviar mensagens interativas
url = "https://gate.whapi.cloud/messages/interactive?token=IggSqEFstZ8K4E7Pt1XMQFGx5bn3a4L5"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer IggSqEFstZ8K4E7Pt1XMQFGx5bn3a4L5"
}

# Parâmetros da mensagem interativa
payload = {
    "to": "5527996012345@s.whatsapp.net",  # Número de telefone do destinatário
    "type": "interactive",
    "interactive": {
        "buttons": [
            {"text": "Sim", "action": "reply", "value": "yes"},
            {"text": "Não", "action": "reply", "value": "no"}
        ],
        "text": "Você gostaria de receber atualizações?"
    }
}
payload = {
    "body": { "text": "string" },
    "footer": { "text": "string" },
    "action": {
        "catalog_id": "string",
        "product_id": "string"
    },
    "to": "5527996012345@s.whatsapp.net"
}

# Envia a mensagem interativa
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Mensagem interativa enviada com sucesso!")
else:
    print("Erro ao enviar a mensagem.")
