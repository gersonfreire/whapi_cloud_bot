import requests

from util_config import api_key, api_url, logger


def send_to_whatsapp(message, whatsapp_recipient, whapi_api_key = api_key, logger = logger,  no_link_preview = True):
    """Sends a message with an image to WhatsApp via the API."""
    headers = {
        'Authorization': f'Bearer {whapi_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'to': whatsapp_recipient,
        "body": message,
        "no_link_preview": no_link_preview,
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        logger.info('Message successfully sent to WhatsApp.')
    else:
        # b'{"error":{"code":402,"message":"trial version limit exceeded"}}'
        # TODO: send alert to ntfy.io or email or telegram
        logger.error(f'Failed to send message. Response code: {response.status_code}')