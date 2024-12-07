from datetime import datetime
import requests
import tzlocal
from cryptography.hazmat.primitives.asymmetric import ed25519
import json
from util import *

def time(endpoint) -> str:
    response = requests.get(link(endpoint)).json()
    timestamp = response['serverTime'] / 1000
    return "[" + datetime.fromtimestamp(timestamp, tzlocal.get_localzone()).strftime("%Y-%m-%d at %H:%M:%S") + "] "
def ping(endpoint):
    return requests.get(link(endpoint)).ok

def sign(keys, endpoints) -> dict:
    signatures = {}
    for end in endpoints:
        endpoint = "/trade/api/v2/" + endpoints[end]
        payload = {}
        unquote = endpoint
        signature_msg = "GET" + unquote + json.dumps(payload, separators=(',', ':'), sort_keys=True)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(keys['secret']))
        signatures[end] = secret_key.sign(bytes(signature_msg, 'utf-8')).hex()
    return signatures
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
    print(f"accessing info on {ticker}...")
    response = requests.get(link(endpoint), headers=headers_no_sign(key),
                            params={"exchange": "coinswitchx", "symbol": symbol}).json()
    if symbol in response['data']['coinswitchx']:
        return True, float(response['data']['coinswitchx'][symbol]['quote']['min'])
    else:
        return False, 0.0


def order(keys):
    endpoint = "/trade/api/v2/order"
    signature = sign(keys, endpoint)
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
        'X-AUTH-APIKEY': keys['api']
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.status_code)
    print(response.text)

def folio_display(portfolio):
    print("displaying portfolio...")
    for ticker in portfolio:
        if ticker == "WALLET":
           print("wallet: ₹" + decimalize(portfolio["WALLET"]['balance']))
           break
        token_display(portfolio[ticker], ticker, False)

    pnl = portfolio["STATS"]['pnl']
    color = num_to_color(pnl)
    pnl = decimalize(pnl)
    pnlp = decimalize(portfolio["STATS"]['pnlp'])
    tax = decimalize(portfolio["STATS"]['tax'])
    total_invest = decimalize(portfolio["STATS"]['total_invest'])
    current_value = decimalize(portfolio["STATS"]['current_value'])

    print("tax paid: ₹" + tax)
    print("total invested: ₹" + total_invest)
    print_color("current value: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", color)
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
    print_color(token['name'] + " ($" + ticker + ")", "yellow")
    print("tokens: ⦿" + balance + " (locked: ⦿" + locked + ")")
    print("invested: ₹" + invested_ex_fee + " + (₹" + fees + " fees) = ₹" + invested)
    print_color("current: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", color)
    print("buy avg: ₹" + buy_avg)
    print("buy now: ₹" + buy_now)
    print_line()