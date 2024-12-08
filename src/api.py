import time, urllib, requests, json, util
from urllib.parse import urlparse, urlencode
from cryptography.hazmat.primitives.asymmetric import ed25519

def server_time(endpoint) -> str:
    response = requests.get(util.link(endpoint)).json()
    return util.chronify(response['serverTime'])
def ping(endpoint):
    return requests.get(util.link(endpoint)).ok

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

    response = requests.post(util.link(endpoint_old), headers = util.headers_epoch(signature,keys['api'],epoch_time), json = payload)
    if response.ok:
        data = response.json()['data']
        return 0, {
            'id': data['order_id'],
            'symbol': data['symbol'],
            'price': data['price'],
            'quantity': data['orig_qty'],
            'time': util.chronify(data['created_time'])
        }
    elif response.status_code == 422:
        return 1, {} #wrong action or token
    elif response.status_code == 424:
        return 2, {} #not enough token
    elif response.status_code == 423:
        return 3, {}  #too less token <150
    else:
        return 4, {}
def sign_candle(ticker, keys, endpoint) -> {bool, dict}:
    endpoint = "/trade/api/v2/" + endpoint
    method = "GET"
    params = {
        "symbol": f"{ticker}/INR",
        "exchange": "coinswitchx"
    }
    payload = {}
    epoch_time = str(int(time.time() * 1000))
    endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
    signature_msg = method + urllib.parse.unquote_plus(endpoint) + epoch_time
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(keys['secret']))
    signature_bytes = secret_key.sign( bytes(signature_msg, 'utf-8'))
    signature = signature_bytes.hex()

    url = "https://coinswitch.co" + endpoint
    response = requests.get(url, headers=util.headers_epoch(signature, keys['api'], epoch_time), json=payload)
    if response.ok:
        data = response.json()['data']['coinswitchx']
        return True , {
            'ticker': ticker,
            'open': data['openPrice'],
            'high': data['highPrice'],
            'low': data['lowPrice'],
            'current': data['lastPrice'],
            'percen': data['percentageChange'],
            'time': util.chronify(data['at'])
        }
    else:
        return False, {}

def tds(key, signature, endpoint) -> {float, str}:
    response = requests.get(util.link(endpoint),headers = util.headers(signature, key))
    data = response.json()['data']
    return float(data['total_tds_amount']), data['financial_year']
def folio(key, signature, endpoint, tax) -> dict:
    portfolio = {}
    payload = {}
    response = requests.get(util.link(endpoint), headers = util.headers(signature, key), json=payload)
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
    response = requests.get(util.link(endpoint), headers=util.headers_no_sign(key),
                            params={"exchange": "coinswitchx", "symbol": symbol}).json()
    if symbol in response['data']['coinswitchx']:
        return True, float(response['data']['coinswitchx'][symbol]['quote']['min'])
    else:
        return False, 0.0
def order(keys, endpoint, action, ticker, quantity, price) -> {int, dict}:
    return sign_order(keys, endpoint, action, f"{ticker.upper()}/INR", price, quantity)

def folio_display(portfolio):
    pnl = portfolio["STATS"]['pnl']
    color = util.num_to_color_bg(pnl)
    color_dark = util.num_to_color_dark(pnl)
    pnl = util.decimalize(pnl)
    pnlp = util.decimalize(portfolio["STATS"]['pnlp'])
    tax = util.decimalize(portfolio["STATS"]['tax'])
    total_invest = util.decimalize(portfolio["STATS"]['total_invest'])
    current_value = util.decimalize(portfolio["STATS"]['current_value'])

    for ticker in portfolio:
        if ticker == "WALLET":
           util.print_color("WALLET", "bold_bg_yellow")
           util.print_color("wallet: ₹" + util.decimalize(portfolio["WALLET"]['balance']), color_dark)
           break
        token_display(portfolio[ticker], ticker, False)

    util.print_color("tax paid: ₹" + tax, color_dark)
    util.print_color("total invested: ₹" + total_invest, color_dark)
    util.print_color("current value: ₹" + current_value + " (" + pnl + ", " + pnlp + " %)", color)
    util.print_line()
def token_display(token,ticker, display_zero):
    balance = util.decimalize(token['balance'])
    locked = util.decimalize(token['locked'])
    invested = util.decimalize(token['invested'])
    invested_ex_fee = util.decimalize(token['invested_ex_fee'])
    current_value = util.decimalize(token['current_value'])
    fees = util.decimalize(token['fees'])

    buy_avg = util.decimalize(token['buy_avg'])
    buy_now = util.decimalize(token['buy_now'])

    pnl = token['pnl']
    color = util.num_to_color(pnl)
    color_dark = util.num_to_color_dark(pnl)
    pnl = util.decimalize(pnl)
    pnlp = util.decimalize(token['pnlp'])

    if (balance == "0.0" and locked == "0.0") and not display_zero:
        return
    util.print_color(token['name'] + " ($" + ticker + ")", "bold_bg_yellow")
    util.print_color("tokens: ⦿" + balance + " (locked: ⦿" + locked + ")", color_dark)
    util.print_color("buy avg: ₹" + buy_avg, color_dark)
    util.print_color("buy now: ₹" + buy_now, color_dark)
    util.print_color("invested: ₹" + invested_ex_fee + " + (₹" + fees + " fees) = ₹" + invested, color_dark)
    util.print_color("current: ₹" + current_value + " (₹" + pnl + ", " + pnlp + " %)", color)
    util.print_line()