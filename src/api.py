from datetime import datetime
import time
import requests
import tzlocal
from cryptography.hazmat.primitives.asymmetric import ed25519
import json
from util import *

def server_time(endpoint) -> str:
    response = requests.get(link(endpoint)).json()
    timestamp = response['serverTime'] / 1000
    return "[" + datetime.fromtimestamp(timestamp, tzlocal.get_localzone()).strftime("%Y-%m-%d at %H:%M:%S") + "] "
def ping(endpoint):
    return requests.get(link(endpoint)).ok

def sign(keys, endpoints) -> dict:
    signatures = {}
    for end in endpoints:
        if end == 'order':
            continue
        endpoint = "/trade/api/v2/" + endpoints[end]
        payload = {}

        signature_msg = "GET" + endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(keys['secret']))
        signatures[end] = secret_key.sign(bytes(signature_msg, 'utf-8')).hex()

    return signatures
def sign_order(keys, endpoint, action, symbol, price, quantity) -> {int, dict}:
    endpoint_old = endpoint
    endpoint = "/trade/api/v2/" + endpoint
    payload = {
        "side": action,
        "symbol": symbol + "/INR",
        "type": "limit",
        "price": price,
        "quantity": quantity,
        "exchange": "coinswitchx"
    }

    epoch_time = str(int(time.time() * 1000))

    signature_msg = "POST" + endpoint + epoch_time
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(keys['secret']))
    signature = secret_key.sign(bytes(signature_msg, 'utf-8')).hex()

    response = requests.post(link(endpoint_old), headers = headers_epoch(signature,keys['api'],epoch_time), json = payload)
    if response.ok:
        data = response.json()['data']
        return 0, {
            'id': data['order_id'],
            'symbol': data['symbol'],
            'price': data['price'],
            'quantity': data['orig_qty'],
        }
    elif response.status_code == 422:
        return 1, {} #wrong action or token
    elif response.status_code == 424:
        return 2, {} #not enough token
    elif response.status_code == 423:
        return 3, {}  #too less token <150
    else:
        return 4, {}

def tds(key, signature, endpoint) -> {float, str}:
    response = requests.get(link(endpoint),headers = headers(signature, key))
    data = response.json()['data']
    return float(data['total_tds_amount']), data['financial_year']
def folio(key, signature, endpoint, tax) -> dict:
    portfolio = {}
    payload = {}
    response = requests.get(link(endpoint), headers = headers(signature, key), json=payload)
    coin_list = json.loads(response.text)['data']
    total_invest = current_invest_value = 0.0

    for coin in coin_list:
        ticker = coin['currency']
        name = coin['name']
        balance = float(coin['main_balance'])

        if ticker == "INR":
            portfolio["WALLET"] = {
                'name' : name,
                'balance' : balance,
            }
            continue

        locked = float(coin['blocked_balance_order'])
        buy_avg = float(coin['buy_average_price'])
        invested = float(coin['invested_value'])
        invested_ex_fee = float(coin['invested_value_excluding_fee'])
        current_value = float(coin['current_value'])
        buy_now = float(coin['buy_rate'])

        fees = invested - invested_ex_fee
        pnl = current_value - invested
        pnlp = (pnl/ invested) * 100.0

        total_invest += invested
        current_invest_value += current_value

        portfolio[ticker] = {
            'name' : name,
            'balance' : balance,
            'locked' : locked,
            'buy_avg' : buy_avg,
            'invested' : invested,
            'invested_ex_fee' : invested_ex_fee,
            'current_value' : current_value,
            'buy_now' : buy_now,
            'fees' : fees,
            'pnl' : pnl,
            'pnlp' : pnlp
        }
    total_pnl = current_invest_value - total_invest
    total_pnlp = (total_pnl / total_invest) * 100.0
    portfolio['STATS'] = {
        'total_invest' : total_invest,
        'current_value' : total_invest,
        'pnl' : total_pnl,
        'pnlp' : total_pnlp,
        'tax' : tax
    }
    return portfolio
def info(ticker, key, endpoint) -> {bool, float}:
    symbol = f"{ticker.upper()}/INR"
    response = requests.get(link(endpoint), headers=headers_no_sign(key),
                            params={"exchange": "coinswitchx", "symbol": symbol}).json()
    if symbol in response['data']['coinswitchx']:
        return True, float(response['data']['coinswitchx'][symbol]['quote']['min'])
    else:
        return False, 0.0
def order(keys, endpoint, action, ticker, quantity, price) -> {int, dict}:
    return sign_order(keys, endpoint, action, f"{ticker.upper()}/INR", price, quantity)

def folio_display(portfolio):
    for ticker in portfolio:
        if ticker == "WALLET":
           print("wallet: ₹" + decimalize(portfolio["WALLET"]['balance']))
           break
        token_display(portfolio[ticker], ticker, False)

    pnl = portfolio["STATS"]['pnl']
    color = num_to_color_bg(pnl)
    pnl = decimalize(pnl)
    pnlp = decimalize(portfolio["STATS"]['pnlp'])
    tax = decimalize(portfolio["STATS"]['tax'])
    total_invest = decimalize(portfolio["STATS"]['total_invest'])
    current_value = decimalize(portfolio["STATS"]['current_value'])

    print("tax paid: ₹" + tax)
    print("total invested: ₹" + total_invest)
    print_color("current value: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", color)
    print_line()
def token_display(token,ticker, display_zero):
    balance = decimalize(token['balance'])
    locked = decimalize(token['locked'])
    invested = decimalize(token['invested'])
    invested_ex_fee = decimalize(token['invested_ex_fee'])
    current_value = decimalize(token['current_value'])
    fees = decimalize(token['fees'])

    buy_avg = decimalize(token['buy_avg'])
    buy_now = decimalize(token['buy_now'])

    pnl = token['pnl']
    color = num_to_color(pnl)
    pnl = decimalize(pnl)
    pnlp = decimalize(token['pnlp'])

    if (balance == "0.0" and locked == "0.0") and not display_zero:
        return
    print_color(token['name'] + " ($" + ticker + ")", "bold_bg_yellow")
    print("tokens: ⦿" + balance + " (locked: ⦿" + locked + ")")
    print("buy avg: ₹" + buy_avg)
    print("buy now: ₹" + buy_now)
    print("invested: ₹" + invested_ex_fee + " + (₹" + fees + " fees) = ₹" + invested)
    print_color("current: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", color)
    print_line()