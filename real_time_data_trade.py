import websocket
import json
import time
import requests
import hashlib
import jwt
import uuid
from urllib.parse import urlencode
import os

try:
    import thread
except ImportError:
    import _thread as thread

API_KEY = 'rNUMn2obU9jy4jupd2ZckmKjhdjDtZHmxGjxFHIX'
SECRET_KEY = 'FF34Txz0QS8rH0xOi2YmYFtiouxyARYPW6nvXhJ9'

price = 0


def on_message(ws, message):
    json_data = json.loads(message)
    global price
    if price == 0:
        price = json_data['trade_price']
        print(price)
        print('코인의 가격 설정')
    else:
        percent = (price - json_data['trade_price']
                   ) / json_data['trade_price'] * 100
        print(price)
        print('시작 가격보다 ', percent, '변화')
        if percent > 0:
            query = {
                'market': 'KRW-BTC',
                'side': 'bid',
                'volume': '0.0002',
                'price': json_data['trade_price'],
                'ord_type': 'limit',
            }
            query_string = urlencode(query).encode()

            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()

            payload = {
                'access_key': API_KEY,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }

            jwt_token = jwt.encode(payload, SECRET_KEY).decode('utf-8')
            authorize_token = 'Bearer {}'.format(jwt_token)
            headers = {"Authorization": authorize_token}

            res = requests.post(
                'https://api.upbit.com/v1/orders', params=query, headers=headers)
            print(res.json())


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("## closed ##")


def on_open(ws):
    def run(*args):
        ws.send(json.dumps(
            [{"ticket": "test"}, {"type": "ticker", 'codes': ["KRW-BTC"]}]))
    thread.start_new_thread(run, ())


websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://api.upbit.com/websocket/v1",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
print(ws.on_open)
ws.run_forever()
