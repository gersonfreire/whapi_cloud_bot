import json
import socket
import ssl
from flask import Flask, request, jsonify
import requests

import sys, os

import util_polls

# Add the parent folder path to the sys.path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

script_folder = os.path.dirname(os.path.abspath(__file__))

import util_crypto

from apscheduler.schedulers.background import BackgroundScheduler

# Enable logging
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

version = '0.6.0 Fixed decimal trigger'

# ----------------------------------------------
# Defina as configurações da API
api_url = "https://gate.whapi.cloud/messages/text"

api_key = "IggSqEFstZ8K4E7Pt1XMQFGx5bn3a4L5" 
zap_sender = '+5527996012345'  

# ----------------------------------------------

# Argumento de linha de comando especifica o bot a ser usado
if ('PantheonBot' in sys.argv):
    api_key = "oNDMmznkXP2LPYgCVoSuQtNbGjBClCds" 
    zap_sender = '+5527998881234' 
elif ('SandBot' in sys.argv):
    api_key = "jVqSRfBPiqylCzm6BD3lfqVeWRK20jJM"
    zap_sender = '+5527998881234'  

# ----------------------------------------------
# Carrega triggers.json

triggers = {}
# if triggers json file exists, load it into triggers object
trigger_file = f'{script_folder}{os.sep}triggers.json'
if os.path.exists(trigger_file):
    with open(trigger_file, 'r') as f:
        triggers = json.load(f)

# ----------------------------------------------
# Carrega configurações API Foxbit api_key etc do arquivo foxbit.json
foxbit_settings = {}
# if foxbit json file exists, load it into foxbit object
foxbit_file = f'{script_folder}{os.sep}foxbit.json'
if os.path.exists(foxbit_file):
    with open(foxbit_file, 'r') as f:
        foxbit_settings = json.load(f)

# ----------------------------------------------

help_message = """*Olá! Eu sou um bot que te ajuda a gerenciar criptomoedas.*

- _Para saber o preço de uma criptomoeda, digite:_
`/price <sigla da criptomoeda> <moeda-para-conversão>`

- _Os defaults, caso omitidos, são:_ `BTC BRL` _(Bitcoin em Reais)_

- _Por exemplo, para saber a cotação do Bitcoin em Reais, digite:_
`/price`

- _Para saber a cotação do Bitcoin em Dólares, digite:_
`/price BTC USD`

- _Para ver a lista de todas as criptomoedas disponíveis, digite:_
`/cryptos`

- _Para pesquisar uma crypto pelo nome digite:_
`/cryptos <nome-do-crypto-a-pesquisar>`

- _Por exemplo, para pesquisar por Ethereum, digite:_
`/cryptos ethereum`

- _Para criar um gatilho de alta (up) ou de baixa (down), digite:_
  `/trigger <sigla-da-cripto> <preço-de-disparo> <up | down>`

- _Por exemplo, para criar um gatilho de alta para Bitcoin a R$ 300.000, digite:_
`/trigger btc 300000 up`

- _Para mostrar o gatilho ativo, digite:_ 
`/trigger list`

- _Para desativar todos os gatilhos, digite:_ 
`/trigger off` 

- _Para desativar os gatilhos up e down de uma crypto especifica, digite:_ 
`/trigger off <symbolo-da-cripto>`

- _Exemplo para desativar todos os gatilhos do BTC:_ 
`/trigger off btc`  

- _Versão para Telegram:_ https://t.me/BigQuoteBot
"""

def save_triggers():
    with open(trigger_file, 'w') as f:
        json.dump(triggers, f, indent=4)
    
def save_foxbit_settings(foxbit_settings):
    with open(foxbit_file, 'w') as f:
        json.dump(foxbit_settings, f, indent=4)

def load_triggers():
    global triggers
    with open(trigger_file, 'r') as f:
        triggers = json.load(f)
    
def load_foxbit_settings():
    with open(foxbit_file, 'r') as f:
        foxbit_settings = json.load(f)
