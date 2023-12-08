import json
import os
import ssl
import websocket as wb

from binance.client import Client
from datetime import datetime
from insert_data import create_table
from sql import Session

from price_data import CryptoPrice
from pprint import pprint
from dotenv import load_dotenv

closed_prices = []
load_dotenv()
create_table()
session = Session()

BINANCE_SOCKET = "wss://stream.binance.com:9443/stream?streams=bnbusdt@kline_1m/ethusdt@kline_1m/btcusdt@kline_1m/ltcusdt@kline_1m"
API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET, tld='us')


def on_open(wsapp):
    print("connection opened")


def on_close(wsapp, close_status_code, close_msg):
    print("closed connection")
    if close_status_code or close_msg:
        print("close status code: " + str(close_status_code))

        print("close message: " + str(close_msg))


def on_error(wsapp, error_code):
    print(error_code)


def on_message(wsapp, message):
    global closed_prices

    message = json.loads(message)
    pprint(message)
    candle = message['data']['k']
    is_candle_closed = candle['x']

    if is_candle_closed:
        symbol = candle['s']
        closed = candle['c']
        open = candle['o']
        high = candle['h']
        low = candle['l']
        volume = candle['v']
        pprint(f"closed: {closed}")
        pprint(f"open: {open}")
        pprint(f"high: {high}")
        pprint(f"low: {low}")
        pprint(f"volume: {volume}")
        closed_prices.append(float(closed))

        crypto = CryptoPrice(ticker=symbol, open_price=open, close_price=closed,
                             high_price=high, low_price=low, volume=volume, time=datetime.utcnow())
        try:
            session.add(crypto)
            session.commit()
        except Exception as err:
            pprint(err)
            session.rollback()
        session.close()


ws = wb.WebSocketApp(BINANCE_SOCKET, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
