
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode
import requests

from util_config import logger

api_key = 'y3TxQSNOs2qnr6whWQsaeuixsTgBfE1jUiSLG71a'# readonly os.getenv('FOXBIT_API_KEY')
api_key = 'z2XOZ29JxpJsweVbm7Jp8ewfdjEGgi0tCyFVxekN'# poc rw os.getenv('FOXBIT_API_KEY')
api_secret =  'NummwUlhO5790AjruTaSvoBPikfI6rzYPTtf24Vw' # readonly os.getenv('FOXBIT_API_SECRET')
# Get environment variables
API_KEY = 'x3TxQSNOs2qnr6whWQsaeuixsTgBfE1jUiSLG71w' # ro  # os.getenv("API_KEY")
API_KEY = 'z2XOZ29JxpJsweVbm7Jp8ewfdjEGgi0tCyFVxekM' # rw  # os.getenv("API_KEY")
API_SECRET = 'Pma5uFhSu1bfhitEf4RPD4xAzveozYOKrriAXHHS' # ro  # os.getenv("API_SECRET")
API_SECRET = 'NummwUlhO5790AjruTaSvoBPikfI6rzYPTtf24VY' # rw  # os.getenv("API_SECRET")

USERID = '31198946922749' # readonly os.getenv("FOXBIT_USERID")
USERNAME = 'fulano@gmail.com' # os.getenv("FOXBIT_USERNAME")
PASSWORD = 'mypassword' #os.getenv("FOXBIT_PASSWORD")

api_base_url = 'https://api.foxbit.com.br'


def sign(method, path, params, body):
    queryString = ''
    if params:
        queryString = urlencode(params)

    rawBody = ''
    if body:
        rawBody = json.dumps(body)

    timestamp = str(int(time.time() * 1000))
    preHash = f"{timestamp}{method.upper()}{path}{queryString}{rawBody}"
    print('PreHash:', preHash)
    signature = hmac.new(api_secret.encode(), preHash.encode(), hashlib.sha256).hexdigest()
    print('Signature:', signature)

    return signature, timestamp

def request(method, path, params, body):
    print('--------------------------------------------------')
    print('Requesting:', method, path)
    signature, timestamp = sign(method, path, params, body)
    url = f"{api_base_url}{path}"
    headers = {
        'X-FB-ACCESS-KEY': api_key,
        'X-FB-ACCESS-TIMESTAMP': timestamp,
        'X-FB-ACCESS-SIGNATURE': signature,
        'Content-Type': 'application/json',
    }

    try:
        response = requests.request(method, url, params=params, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        # '{"error":{"message":"Bad request.","code":400,"details":["price must be a decimal number represented as string","price must be a number string"]}}'
        print(f"HTTP Status Code: {http_err.response.status_code}, Error Response Body:", http_err.response.json())
        raise
    except Exception as err:
        print(f"An error occurred: {err}")
        raise

# Get user info
def get_user_info(api_key=api_key, api_secret=api_secret, api_base_url=api_base_url):
    try:
        meResponse = request('GET', '/rest/v3/me', None, None)
        logger.debug('Response:', meResponse)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        
    return meResponse

def get_orders(api_key=api_key, api_secret=api_secret, api_base_url=api_base_url):
    try:
        ordersResponse = request('GET', '/rest/v3/orders', None, None)
        logger.debug('Response:', ordersResponse)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return ordersResponse

def create_order(side, quantity,market_symbol='btcbrl', type = 'MARKET', api_key=api_key, api_secret=api_secret, api_base_url=api_base_url,  price=0):
    try:
        order = {
            'market_symbol': market_symbol,
            'side': side,
            'type': type,
            # 'price': str(price),
            'quantity': str(quantity),
        }
        # order = {
        #     "side": "BUY",
        #     "type": "MARKET",
        #     "market_symbol": "btcbrl",
        #     # "client_order_id": "351637946500",
        #     #"remark": "A remarkable note for the order.",
        #     "quantity": "0.000003125" # "0.42"
        # }   
        orderResponse = request('POST', '/rest/v3/orders', None, order)
        logger.debug('Response:', orderResponse)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return orderResponse

# List Foxbit orders
def test_foxbit():

    try:
        quantity = "0.000003125"
        # order_response = create_order('BUY', quantity)
        # logger.debug(order_response)
                
        print('FOXBIT_API_KEY:', api_key)

        # Get user info
        meResponse = request('GET', '/rest/v3/me', None, None)
        print('Response:', meResponse)

        # List orders
        ordersResponse = request('GET', '/rest/v3/orders', None, None)
        print('Response:', ordersResponse)

        # Create a new order
        # https://docs.foxbit.com.br/rest/v2/#/paths/~1AP~1SendOrder/get
        # https://api.foxbit.com.br/AP/SendOrder
        # https://docs.foxbit.com.br/rest/v3/#tag/Trading/operation/OrdersController_create
        order = {
            "side": "BUY",
            "type": "MARKET",
            "market_symbol": "btcbrl",
            "client_order_id": "251637946509",
            "remark": "A remarkable note for the order.",
            "quantity": "0.42"
        }  
        order = {
        "side": "BUY",
        "type": "INSTANT",
        "market_symbol": "btcbrl",
        "client_order_id": "351637946500",
        "remark": "A remarkable note for the order.",
        "amount": "1000.0"
        }   
        order = {
            "side": "BUY",
            "type": "MARKET",
            "market_symbol": "btcbrl",
            "client_order_id": "351637946500",
            "remark": "A remarkable note for the order.",
            "quantity": "0.000003125" # "0.42"
        }                   

        orderResponse = request('POST', '/rest/v3/orders', None, order)
        print('Response:', orderResponse)

        """
        Create an order
        Create an order with the specified characteristics
        Required API Key permissions: trade
        Rate Limit: This endpoint has the limit of 30 requests per 2 seconds. An order, after created can be presented in the following states:

        State	Description
        ACTIVE	The order is in the matching queue, waiting for deal
        PARTIALLY_FILLED	A part of the order has been filled and it is in the matching queue, waiting for deal
        FILLED	The order is already traded and not in the matching queue anymore
        PARTIALLY_CANCELED	The order is not in the matching queue anymore The order was partially traded, but the remaining was canceled
        CANCELED	The order is not in the matching queue anymore and is completely canceled There is no trade associated with this order        
        """
        
        # order = {
        #     "InstrumentId": 1,
        #     "OMSId": 1,
        #     "AccountId": 1,
        #     "TimeInForce": 1,
        #     "ClientOrderId": 1,
        #     "OrderIdOCO": 0,
        #     "UseDisplayQuantity": False,
        #     "Side": 0,
        #     "quantity": 1,
        #     "OrderType": 2,
        #     "PegPriceType": 3,
        #     "LimitPrice": 8800
        # }  
        # {
        #     'market_symbol': 'btcbrl',
        #     'side': 'BUY',
        #     'type': 'LIMIT',
        #     'price': '10.0',
        #     'quantity': '0.0001',
        # }

        time.sleep(2)

        # Get active orders
        ordersParams = {
            'market_symbol': 'btcbrl',
            'state': 'ACTIVE'
        }
        ordersResponse = request('GET', '/rest/v3/orders', ordersParams, None)
        print('Response:', ordersResponse)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    return ordersResponse

if __name__ == '__main__':

    try:

        test_foxbit()

        response = get_user_info()
        logger.debug(f"Response: {response}")

        response = get_orders()
        logger.debug(f"Response: {response}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")