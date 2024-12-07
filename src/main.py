from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlparse, urlencode
import urllib
import json
import requests
import os
import tzlocal

from dotenv import load_dotenv
from datetime import datetime

def link(end) -> str:
    return "https://coinswitch.co" +  end
def envs():
    load_dotenv()
    print("loaded api keys!")
    return os.getenv("API"),os.getenv("SECRET")
def colo(text, color):
    print({'green': '\x1b[6;30;42m', 'red': '\x1b[6;30;41m', 'yellow': '\x1b[5;30;43m'}.get(color, '') + text + '\x1b[0m')
def rond(val) -> str:
    rounded = float(int(float(val) * 1000.0))/1000.0
    return str(rounded)
def time() -> str:
    response = requests.get(link("/trade/api/v2/time")).json()
    timestamp = response['serverTime'] / 1000
    return datetime.fromtimestamp(timestamp, tzlocal.get_localzone()).strftime("%Y-%m-%d %H:%M:%S.%f (%Z)")
def ping():
    url = link("/trade/api/v2/ping")
    if requests.get(url).ok:
        print(f"pinged {link("")} at {time()}"); return
    print(f"could not ping {link("")} at {time()}")

def sign(key, endpoint) -> str:
    params = {}
    url = link(endpoint)
    method = "GET"
    payload = {}
    unquote = endpoint
    if len(params) != 0:
        endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote = urllib.parse.unquote_plus(endpoint)
    signature_msg = method + unquote + json.dumps(payload, separators=(',', ':'), sort_keys=True)

    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(key[1])
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': key[0]
    }
    response = requests.request(method, url, headers=headers, json=payload)
    if response.status_code == 200:
        return signature

def taxs(key):
    endpoint = "/trade/api/v2/tds"
    signature = sign(key, endpoint)
    url = link(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': key[0]
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    data = json.loads(response.text)['data']
    tds = data['total_tds_amount']
    year = data['financial_year']
    print("tax paid " + year + ": ₹" + rond(tds))
def port(key):
    print("accessing portfolio...\n")
    endpoint = "/trade/api/v2/user/portfolio"
    signature = sign(key, endpoint)
    url = link(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': key[0]
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    if response.status_code != 200:
        return
    coin_list = json.loads(response.text)['data']
    total_invest = 0.0
    current_invest = 0.0
    for coin in coin_list:
        ticker = coin['currency']
        name = coin['name']
        balance = rond(coin['main_balance'])
        if ticker == "INR":
            pnl = current_invest - total_invest
            pnlp = ((pnl / total_invest) * 100.0)
            colour = 'green'
            if pnlp < 0:
                colour = 'red'
            pnl = rond(str(pnl))
            pnlp = rond(str(pnlp))
            print("wallet: ₹" + balance)
            print("total invested: ₹" + rond(str(total_invest)))
            colo("current value: ₹" + rond(str(current_invest)) + " (" + pnl + ", " + pnlp + " %)", colour)
            taxs(key)
            print("==================================")
            break
        locked = rond(coin['blocked_balance_order'])
        avg_price = rond(coin['buy_average_price'])
        invested = rond(coin['invested_value'])
        invested_ex_fee = rond(coin['invested_value_excluding_fee'])
        current_value = rond(coin['current_value'])
        buy_rate = rond(coin['buy_rate'])
        fees = rond(str(float(invested) - float(invested_ex_fee)))
        pnl = rond(str(float(current_value) - float(invested)))
        pnlp = rond((float(pnl) / float(invested)) * 100.0)
        total_invest += float(invested)
        current_invest += float(current_value)
        colour = 'green'
        if float(pnlp) < 0:
            colour = 'red'
        colo(name + " (" + ticker + ")", "yellow")
        print("tokens: ⦿" + balance + " (locked: ⦿" + locked + ")")
        print("invested: ₹" + invested_ex_fee + " + (₹" + fees + " fees) = ₹" + invested)
        colo("current: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", colour)
        print("buy avg: ₹" + avg_price)
        print("buy now: ₹" + buy_rate)
        print("==================================")

def info(key, ticker):
    url = link("/trade/api/v2/tradeInfo")
    symbol = f"{ticker.upper()}/INR"
    print(f"accessing info on {ticker}...")

    response = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': key[0]
        },
        params={
            "exchange": "coinswitchx",
            "symbol": symbol
        }
    )
    minim = response.json()['data']['coinswitchx'][symbol]['quote']['min']
    print(f"min sell amt: ₹{minim}.0")
    print("==================================")
    return float(minim)
def order(key):
    endpoint = "/trade/api/v2/order"
    signature = sign(key, endpoint)
    url = link(endpoint)

    payload = {
        "side": "sell",
        "symbol": "ETH/INR",
        "type": "limit",
        "price": 15000,
        "quantity": 0.004,
        "exchange": "coinswitchx"
    }

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': key[0]
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.status_code)
    print(response.text)

def main():
    key = envs()
    ping()
    port(key)
    info(key, "RENDER")
    info(key, "ETH")
    order(key)

main()