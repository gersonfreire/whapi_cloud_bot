# !/usr/bin/env python

from util_config import *
from util_whapi_cloud import send_to_whatsapp
import util_foxbit
 
# ----------------------------------------------

# Ignore specific numbers from the list of numbers
ignore_numbers = ['5527999999999', '5511888888888']
allow_numbers = ['5511999999999', '5511888888888']

dir_name = f'{script_folder}{os.sep}json'
if not os.path.exists(dir_name):
    # Create the directory
    os.makedirs(dir_name)
    
ignore_file = f'{dir_name}{os.sep}ignore.json'
if not os.path.exists(ignore_file):
    # open or create file if not exists
    with open(ignore_file, 'x') as f:
        json.dump(ignore_numbers, f, indent=4)


allow_file = f'{dir_name}{os.sep}allow.json'
if not os.path.exists(allow_file):
    # open or create file if not exists
    with open(allow_file, 'x') as f:
        json.dump([], f, indent=4)        

# ----------------------------------------------

def check_trigger():
    app.logger.info("Checking trigger...")

    for wa_id, trigger in triggers.items():

        for crypto_symbol, trigger_data in trigger.items():
            for trigger_type, trigger_data in trigger_data.items():
                trigger_price = float(trigger_data['price'])

                crypto_price = util_crypto.get_price_crypto(crypto_symbol, 'BRL')

                if (trigger_type == 'up') and (crypto_price > float(trigger_price)):
                    msg_body = f"*Trigger de alta ativado para {crypto_symbol}! R$ {crypto_price} > R$ {trigger_price}*"
                    app.logger.info(msg_body)
                    send_to_whatsapp(msg_body, wa_id)            

                elif (trigger_type != 'up') and (crypto_price < float(trigger_price)):
                    msg_body = f"*Trigger de baixa ativado para {crypto_symbol}! R$ {crypto_price} < R$ {trigger_price}*"
                    app.logger.info(msg_body)
                    send_to_whatsapp(msg_body, wa_id)

seconds = 60*10
# search the list of command line arguments for the word interval and get the next item
filtered_strings = [interval_argument for interval_argument in sys.argv if 'interval' in interval_argument]
if (len(filtered_strings) > 0) and (len(filtered_strings[0].split('=')) > 0) and (filtered_strings[0].split('=')[1].isnumeric()):
    seconds = int(filtered_strings[0].split('=')[1])

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_trigger, trigger="interval", seconds=seconds)
scheduler.start()

app = Flask(__name__)

# -----------

# Função para processar mensagens recebidas
def process_message(message):
  """
  Processa uma mensagem recebida do usuário.

  Args:
    mensagem: A mensagem recebida.
  """

  response_message = "_Desculpe, não entendi o que você quis dizer. Tente novamente ou digite /help para ver as opções disponíveis._"

  # Recupere a mensagem do usuário
  incoming_msg = message["text"]["body"]
  from_number = message["from"]
  logging.info(f"Received message: {incoming_msg} from {from_number}")

  foxbit_user_setings = {
        'api_key': foxbit_settings.get('api_key', ''),
        'api_secret': foxbit_settings.get('api_secret', ''),
  }     

  response_message = """_Desculpe, não entendi o que você quis dizer. Tente novamente ou digite_ `/help` _para ver as opções disponíveis._"""

  if '/price' in incoming_msg:

        crypto_symbol = incoming_msg.split()[1].upper() if len(
            incoming_msg.split()) > 1 else 'BTC'
        currency_price = incoming_msg.split()[2].upper() if len(
            incoming_msg.split()) > 2 else 'BRL'
        price_message = util_crypto.get_price_message(
            crypto_symbol, currency_price)

        response_message = f'_{price_message}_'

  elif '/cryptos' in incoming_msg:

        max_message_length = 1000  # 1600

        page_number = 0
        filter_by = None
        if len(incoming_msg.split()) > 1:
            if incoming_msg.split()[1].isnumeric():
                page_number = int(incoming_msg.split()[1]) - 1
            else:
                filter_by = incoming_msg.split()[1]

        if len(incoming_msg.split()) > 2:
            filter_by = incoming_msg.split()[2]

        cryptos_list = util_crypto.get_crypto_list(filter_by=filter_by)

        if len(cryptos_list) > max_message_length:

            crypto_pages = [cryptos_list[i:i+max_message_length]
                            for i in range(0, len(cryptos_list), max_message_length)]

            # exibe apenas as primeiras 3 paginas
            for page in crypto_pages[page_number: page_number + 3]:

                app.logger.info(f'page: {page}')
                response_message = f'_Total de Cryptos:_ *{len(cryptos_list)}*\n_Página:_ *{page_number+1}/{
                    len(crypto_pages)}*\n\n{crypto_pages[page_number]}...'
                response_message += '\n\nPara ver mais, digite `/cryptos <pagina>`, Ex.: `/cryptos 5`, etc.'

                send_to_whatsapp(response_message, from_number, api_key, logging)
                
                page_number += 1

        else:
            app.logger.info(f'{cryptos_list}')
            response_message = f"""_Total de Cryptos:_ *{len(cryptos_list)}*"""
            response_message = f"""_Página:_ *1/1*
  {cryptos_list}"""
            
            send_to_whatsapp(response_message, from_number, api_key, logging)
            
        return

  elif '/help' in incoming_msg:
        response_message = help_message

  elif '/start' in incoming_msg:
        response_message = help_message

  elif '/about' in incoming_msg:
    
        response_message = 'Este bot foi desenvolvido por Gerson Amorim.'

  elif '/trigger' in incoming_msg:

        response_message = f""" - _Para criar um gatilho, digite:_
  `/trigger <sigla-da-cripto> <preço> <up | down>`

  _Para desativar, digite:_ `/trigger off`
  """

        if (len(incoming_msg.split()) > 1) and (incoming_msg.split()[1] == 'off'):

            # caso o comando seja /trigger off <symbol>
            if len(incoming_msg.split()) > 2:
                crypto_symbol = incoming_msg.split()[2].upper()
                triggers[from_number].pop(crypto_symbol, None)
                response_message = f"""_Gatilho para {crypto_symbol} desativado._"""

            else:                
                triggers.pop(from_number, None)
                response_message = f"""_Todos os seus gatilhos foram desativados._"""

        elif (len(incoming_msg.split()) > 1) and (incoming_msg.split()[1] == 'list'):        
            if not from_number in triggers:
                response_message = f"""_Nenhum gatilho ativo._"""
            else:
                # triggers_list = [f"{trigger['crypto']} {trigger['price']} {trigger['type']}" for trigger in triggers.values() if from_number in triggers]

                triggers_number = triggers[from_number]
                triggers_list = []
                for crypto_symbol, trigger in triggers_number.items():
                    for trigger_type, trigger_data in trigger.items():
                        triggers_list.append(f"{crypto_symbol}  {trigger_type} {trigger_data['price']}")

                triggers_joint = '\n'.join(triggers_list)
                response_message = f"""_Gatilhos ativos:_\n{triggers_joint}"""

        elif len(incoming_msg.split()) > 3:

            crypto_symbol = incoming_msg.split()[1].upper() if len(
                incoming_msg.split()) > 1 else 'BTC'
            trigger_price = float(incoming_msg.split()[2].replace(',','.')) if ((len(
                incoming_msg.split()) > 2) and (str(incoming_msg.split()[2]).replace('.', '').replace(',','').isdecimal()) ) else 0
            trigger_type = incoming_msg.split()[3] if len(
                incoming_msg.split()) > 3 else 'up'

            if str(trigger_price).replace(',','.').replace('.','').isdecimal():
                
                # triggers[from_number] = {'crypto': crypto_symbol, 'price': trigger_price, 'type': trigger_type, 'sender': zap_sender}

                if not from_number in triggers:
                    triggers[from_number] = {
                        crypto_symbol: {
                            trigger_type: {
                                'price': trigger_price,
                                'sender': zap_sender
                            }
                        }
                    }
                else:
                    if not crypto_symbol in triggers[from_number]:
                        triggers[from_number][crypto_symbol] = {
                            trigger_type: {
                                'price': trigger_price,
                                'sender': zap_sender
                            }
                        }
                    else:
                        triggers[from_number][crypto_symbol][trigger_type] = {
                            'price': trigger_price,
                            'sender': zap_sender
                        }

                if trigger_type == 'up':
                    response_message = f"""_Gatilho de alta para {
                        crypto_symbol} configurado para:_ *R$ {trigger_price}*"""
                    response_message += f"""\n_Para desativar, digite:_ `/trigger off`"""
                else:
                    response_message = f"""_Gatilho de baixa para {
                        crypto_symbol} configurado para:_ *R$ {trigger_price}*"""
                    response_message += f"""\n_Para desativar, digite:_ `/trigger off`"""
  
        # save updated triggers object to json file
        with open(trigger_file, 'w') as f:
            json.dump(triggers, f, indent=4)

  elif '/version' in incoming_msg:
        response_message = f"""_CryptoBot Versão:_ `{version}`
_Para mais informações, digite_ `/help`"""

  elif '/foxbit api_key' in incoming_msg:
        
        # global foxbit_settings
        
        load_foxbit_settings()
        if from_number in foxbit_settings:
            foxbit_user_setings = foxbit_settings.get(from_number, {})
        if (from_number in foxbit_settings) and ('api_key' in foxbit_user_setings):
            response_message = f"""_FOXBIT_API_KEY:_ `{foxbit_user_setings['api_key']}`"""
        
        if len(incoming_msg.split()) > 2:
            new_api_key = incoming_msg.split()[2]
            foxbit_user_setings['api_key'] = new_api_key
            foxbit_settings[from_number] = foxbit_user_setings
            response_message = f"""_FOXBIT_API_KEY alterada para:_ `{
                new_api_key}`"""
            
            foxbit_settings[from_number] = foxbit_user_setings
            save_foxbit_settings(foxbit_settings=foxbit_settings)            

  elif '/foxbit api_secret' in incoming_msg:
        # global foxbit_settings

        load_foxbit_settings()
        if from_number in foxbit_settings:
            foxbit_user_setings = foxbit_settings.get(from_number, {})
        if (from_number in foxbit_settings) and ('api_secret' in foxbit_user_setings):
            response_message = f"""_FOXBIT_API_KEY:_ `{foxbit_user_setings['api_key']}`"""

        if len(incoming_msg.split()) > 2:
            new_api_secret = incoming_msg.split()[2]
            foxbit_user_setings['api_secret'] = new_api_secret
            foxbit_settings[from_number] = foxbit_user_setings
            response_message = f"""_FOXBIT_API_SECRET alterada para:_ `{
                new_api_secret}`"""
            
            foxbit_settings[from_number] = foxbit_user_setings
            save_foxbit_settings(foxbit_settings=foxbit_settings)

  elif '/foxbit' in incoming_msg:

    response_message = f"""_Integração Foxbit_

    Para visualizar sua api_key atual, digite_ `/foxbit api_key` 

    _Para visualizar sua api_secret atual, digite_ `/foxbit api_secret` 

    _Para alterar sua api_key, digite_ `/foxbit token <nova-api-key>`  

    _Para alterar sua api_secret, digite_ `/foxbit api_secret <nova-api-secret>`   

    _Para visualizar suas ordens de compra, digite_ `/foxbit orders`

    _Para visualizar suas ordens de venda, digite_ `/foxbit orders`

    _Para criar ordens de compra, digite_ `/foxbit orders buy <quantidade> <preço>`

    _Para criar ordens de venda, digite_ `/foxbit orders sell <quantidade> <preço>`


    """   

    if (from_number in foxbit_settings) and ('api_key' in foxbit_user_setings) and ('api_secret' in foxbit_user_setings):

        foxbit_user_setings = foxbit_settings[from_number]
        util_foxbit.api_key = foxbit_user_setings['api_key']
        util_foxbit.api_secret = foxbit_user_setings['api_secret']

        if '/foxbit orders buy' in incoming_msg:
            quantity = incoming_msg.split()[3] if len(incoming_msg.split()) > 3 else 0
            price = incoming_msg.split()[4] if len(incoming_msg.split()) > 4 else 0
            response_message = f"""_Criando ordem de compra..._"""
            order_response = util_foxbit.create_order('BUY', quantity)
            response_message += f"""_Ordem de compra criada:_ {order_response}"""
            
        elif '/foxbit orders' in incoming_msg:
            orders = util_foxbit.get_orders()
            orders_list = orders['data']
            response_message = f"""_Ordens de compra e venda:_\n"""
            for order in orders_list:
                response_message += f"""_{order['id']} {order['side']} {order['quantity_executed']} {order['price_avg']} {order['market_symbol']} {order['type']} {order['created_at']}_\n"""
            # response_message = f"""_Ordens:_ {orders}"""

        foxbit_user_setings['api_key'] = util_foxbit.api_key
        foxbit_user_setings['api_secret'] = util_foxbit.api_secret
        foxbit_settings[from_number] = foxbit_user_setings
        save_foxbit_settings(foxbit_settings=foxbit_settings)            

    else:
        response_message = f"""_Integração Foxbit não configurada!_
_use os comandos:_
`/foxbit api_key <sua_api_key>` para configurar sua api_key
`/foxbit api_secret <sua_api_secret>` para configurar sua api_secret
 """

  if '/poll' in incoming_msg:
      poll_response = util_polls.send_poll(["Opção 1", "Opção 2", "Opção 3", "Opção 4"], from_number,)
      logger.info(f"Poll response: {poll_response}")
      
  else:
    send_to_whatsapp(response_message, from_number, api_key, logging)

# ----------------------------------------------

# Recupere os dados da mensagem
def process_poll_response(id):
    # Add your code here to process the poll response
    pass

@app.route("/bot", methods=["POST", "GET", "PUT", "DELETE"])
def webhook():
    """
    Endpoint do webhook que recebe mensagens do WhatsApp.
    """

    try:
        # Verifique se o tipo de conteúdo da requisição é JSON
        if request.content_type != "application/json":
            return jsonify({"error": "Tipo de conteúdo inválido"}), 400

        data = request.get_json()

        if 'messages' not in data:
            return jsonify({"error": "Mensagens não encontradas"}), 400

        # percorre lista de mensagens recebidas
        for message in data["messages"]:

            # ignore mensagens de si próprio
            if message["from_me"]:
                app.logger.info(f"Ignoring message from self")
                continue
            if ("action" in message['type']) and ('votes' in message['action']) and (len(message['type']['votes']>0)):  # poll
                id = message["action"]["votes"][0]
                process_poll_response(id)

            elif "text" in message['type']:                               

                # carrega a lista de números permitidos do arquivo json
                allow_numbers = []
                if os.path.exists(allow_file):
                    with open(allow_file, 'r') as f:
                        allow_numbers = json.load(f)

                # se usuario enviar comando /allow, adiciona ou remove o número na lista de permissões
                if ('body' in message['text'])  and ('/allow' in message['text']['body']):
                    number_to_allow = message['text']['body'].split()[1] if len(message['text']['body'].split()) > 1 else message["from"]
                    if number_to_allow not in allow_numbers:
                        allow_numbers.append(message["from"])
                    else:
                        allow_numbers.remove(message["from"])

                    with open(allow_file, 'w') as f:
                        json.dump(allow_numbers, f, indent=4)
                    app.logger.info(f"Allowing message from {message['from']} [{allow_numbers}]")

                # caso a mensagem seja comando /ignore, adiciona o número na lista de ignorados
                ignore_numbers = []   
                # carrega a lista de números a serem ignorados do arquivo json
                if os.path.exists(ignore_file):
                    with open(ignore_file, 'r') as f:
                        ignore_numbers = json.load(f)

                if ('body' in message['text'])  and ('/ignore' in message['text']['body']):
                    number_to_ignore = message['text']['body'].split()[1] if len(message['text']['body'].split()) > 1 else message["from"]
                    if number_to_ignore not in ignore_numbers:
                        ignore_numbers.append(message["from"])
                    else:
                        ignore_numbers.remove(message["from"])
                        
                    with open(ignore_file, 'w') as f:
                        json.dump(ignore_numbers, f, indent=4)
                    app.logger.info(f"Ignoring message from {message['from']} [{ignore_numbers}]")  

                # se o numero não estiver na lista de permitidos ou existir na lista de ignorados, não responde
                if (message["from"] not in allow_numbers) or (message["from"] in ignore_numbers):
                    app.logger.info(f"Ignoring message from {message['from']} [{ignore_numbers}]")
                    continue                   

                # Processe a mensagem (envie mensagem de eco)
                process_message(message) # 'k1pLb5jxAl7t-gM4FBxY.IOQ' type action type vote #'WG1vfUZG+d+28AZSX/JWFfrU9dEDCVSGFf0rnDTBtnU='

    except Exception as e:
        app.logger.error(f"Erro ao processar a mensagem: {e}")

    # Retorne uma resposta bem-sucedida
    return jsonify({"status": "ok"})
  
# ----------------------------------------------

if __name__ == "__main__":

    full_chain_path = 'C:\\Certbot\\live\\protheus.monitor.eco.br\\fullchain.pem'
    priv_key_path = 'C:\\Certbot\\live\\protheus.monitor.eco.br\\privkey.pem'
    
    if os.path.exists(full_chain_path) and os.path.exists(priv_key_path):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_cert_chain(certfile=full_chain_path, keyfile=priv_key_path)

        if ('PantheonBot' in sys.argv):
            app.run(ssl_context=context, host='0.0.0.0', port=5002)
        else:
            app.run(ssl_context=context, host='0.0.0.0', port=5001)

    else: 
        app.run(debug=False, port=5001)    

# ----------------------------------------------
# TODO: listar triggers ativos
# TODO: enviar link telegram/app/web

# /foxbit api_key a2XOZ29JxpJsweVbm7Jp8ewfdjEGgi0tCyFVxekM

# /foxbit orders buy 0.000003125