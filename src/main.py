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
def colo(text, color):
    if color == "green":
        print('\x1b[6;30;42m' + text + '\x1b[0m')
    elif color == "red":
        print('\x1b[6;30;41m' + text + '\x1b[0m')
    elif color == "yellow" :
        print('\x1b[5;30;43m' + text + '\x1b[0m')
def rond(val) -> str:
    rounded = float(int(float(val) * 100.0))/100.0
    return str(rounded)

def time() -> str:
    url = link("/trade/api/v2/time")
    response = json.loads(requests.request("GET", url).text)
    timestamp = response['serverTime'] / 1000

    local_time = datetime.fromtimestamp(timestamp,tzlocal.get_localzone())
    return local_time.strftime("%Y-%m-%d %H:%M:%S.%f (%Z)")
def ping() -> bool:
    url = link("/trade/api/v2/ping")

    response =  requests.request("GET", url)
    if response.status_code != 404:
        print("pinged " + url)
        return True
    else:
        print("could not ping " + url)
        return False
def sign(api_key, secret_key, endpoint) -> str|None:
    #if not ping():
    #    return None
    #print("at", time())
    params = {}
    url = link(endpoint)
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
        #print("keys validated, signature generated!")
        return signature
    elif response.status_code == 401: # Invalid Access
        #print("keys are invalid!")
        return None

def port(api_key, secret_key):
    print("accessing portfolio...\n")
    endpoint = "/trade/api/v2/user/portfolio"
    signature = sign(api_key, secret_key, endpoint)
    url = link(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
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
            total_invest = 15170  # amount ive put in so far td
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
            break
        locked = rond(coin['blocked_balance_order'])
        avg_price = rond(coin['buy_average_price'])
        invested = rond(coin['invested_value'])
        invested_ex_fee = rond(coin['invested_value_excluding_fee'])
        current_value = rond(coin['current_value'])
        #sell_rate = coin['sell_rate']
        buy_rate = rond(coin['buy_rate'])
        #is_avg_price_available = coin['is_average_price_available']
        fees = rond(str(float(invested) - float(invested_ex_fee)))
        pnl = rond(str(float(current_value) - float(invested)))
        pnlp = rond((float(pnl) / float(invested)) * 100.0)
        total_invest += float(invested)
        current_invest += float(current_value)
        colour = 'green'
        if float(pnlp) < 0:
            colour = 'red'
        colour(name + " (" + ticker + ")", "yellow")
        print("tokens: ⦿" + balance + " (locked: ⦿" + locked + ")")
        print("invested: ₹" + invested_ex_fee + " + (₹" + fees + " fees) = ₹" + invested)
        colour("current: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", colour)
        print("buy avg: ₹" + avg_price)
        print("buy now: ₹" + buy_rate)
        print("==================================")
    taxs(api_key, secret_key)
def taxs(api_key, secret_key):
    endpoint = "/trade/api/v2/tds"
    signature = sign(api_key, secret_key, endpoint)
    url = link(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
    }
    response = requests.request("GET", url, headers=headers, json=payload)
    data = json.loads(response.text)['data']
    tds = data['total_tds_amount']
    year = data['financial_year']
    print("tax paid " + year + ": ₹" + rond(tds))

def main():
    envs()
    port(os.getenv("API_KEY"), os.getenv("SECRET_KEY"))
main()