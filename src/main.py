from inspect import signature

from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlparse, urlencode
import urllib
import json
import requests
import os
import tzlocal

from dotenv import load_dotenv
from datetime import datetime

def url_concat(end) -> str:
    return "https://coinswitch.co" +  end
def load_env():
    load_dotenv()
    print("loaded api keys!")
def print_colored(text, color):
    if color == "green":
        print('\x1b[6;30;42m' + text + '\x1b[0m')
    elif color == "red":
        print('\x1b[6;30;41m' + text + '\x1b[0m')
    elif color == "yellow" :
        print('\x1b[5;30;43m' + text + '\x1b[0m')
def rounder(val) -> str:
    rounded = float(int(float(val) * 100.0))/100.0
    return str(rounded)


def time() -> str:
    url = url_concat("/trade/api/v2/time")
    response = json.loads(requests.request("GET", url).text)
    timestamp = response['serverTime'] / 1000

    local_time = datetime.fromtimestamp(timestamp,tzlocal.get_localzone())
    return local_time.strftime("%Y-%m-%d %H:%M:%S.%f (%Z)")
def ping() -> bool:
    url = url_concat("/trade/api/v2/ping")

    response =  requests.request("GET", url)
    if response.status_code != 404:
        print("pinged " + url)
        return True
    else:
        print("could not ping " + url)
        return False
def sign(api_key, secret_key) -> str|None:
    if not ping():
        return None
    print("at", time())
    params = {}
    endpoint = "/trade/api/v2/user/portfolio"
    url = url_concat(endpoint)
    method = "GET"
    payload = {}

    unquote_endpoint = endpoint
    if method == "GET" and len(params) != 0:
        endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote_endpoint = urllib.parse.unquote_plus(endpoint)

    signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    if response.status_code == 200:  # Valid Access
        print("keys validated, signature generated!")
        return signature
    elif response.status_code == 401: # Invalid Access
        print("keys are invalid!")
        return None

def coins(api_key, signature):
    params = {
        "exchange": "coinswitchx",
    }
    endpoint = "/trade/api/v2/coins"
    endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
    url = url_concat(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    print(response.json())
def folio(api_key, signature):
    print("accessing portfolio...\n")
    endpoint = "/trade/api/v2/user/portfolio"
    url = url_concat(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    if response.status_code == 200:
        coin_list = json.loads(response.text)['data']

        total_invest = 0.0
        current_invest = 0.0
        for coin in coin_list:
            ticker = coin['currency']
            name = coin['name']
            balance = rounder(coin['main_balance'])
            if ticker != "INR":
                locked = rounder(coin['blocked_balance_order'])
                avg_price = rounder(coin['buy_average_price'])
                invested = rounder(coin['invested_value'])
                invested_ex_fee = rounder(coin['invested_value_excluding_fee'])
                current_value = rounder(coin['current_value'])
                #sell_rate = coin['sell_rate']
                buy_rate = rounder(coin['buy_rate'])
                #is_avg_price_available = coin['is_average_price_available']

                fees = rounder(str(float(invested) - float(invested_ex_fee)))
                pnl = rounder(str(float(current_value) - float(invested)))
                pnlp = rounder((float(pnl) / float(invested)) * 100.0)
                total_invest += float(invested)
                current_invest += float(current_value)

                color = 'green'
                if float(pnlp) < 0:
                    color = 'red'

                print_colored(name + " (" + ticker + ")", "yellow")
                print("tokens: ⦿" + balance + " (locked: ⦿" + locked + ")")
                print("invested: ₹" + invested_ex_fee + " + (₹" + fees + " fees) = ₹" + invested)
                print_colored("current: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", color)
                print("buy avg: ₹" + avg_price)
                print("buy now: ₹" + buy_rate)
                print("---------------------------------")

            else:
                total_invest = 15170 #amount ive put in so far td
                pnl = current_invest - total_invest
                pnlp = ((pnl/total_invest) * 100.0)

                color = 'green'
                if pnlp < 0:
                    color = 'red'

                pnl = rounder(str(pnl))
                pnlp = rounder(str(pnlp))
                print("wallet: " + ticker + " (" + name + ") : ₹" + balance)
                print("total invested: ₹" + rounder(str(total_invest)))
                print_colored("current value: ₹" + rounder(str(current_invest)) + " (" + pnl + ", " + pnlp + " %)", color)
def taxes(api_key, signature):
    endpoint = "/trade/api/v2/tds"
    url = url_concat(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    print(response.json())


def main():
    load_env()
    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("SECRET_KEY")
    sig = sign(api_key, secret_key)

    folio(api_key,sig)
    taxes(api_key, sig)


if __name__=="__main__":
    main()