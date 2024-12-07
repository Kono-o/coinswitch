import os
from dotenv import load_dotenv

def env():
    load_dotenv()
    return {'api': os.getenv("API"), 'secret': os.getenv("SECRET")}

def link(end) -> str:
    return "https://coinswitch.co/trade/api/v2/" +  end

def print_color(text, color):
    print({'green': '\x1b[6;30;42m', 'red': '\x1b[6;30;41m', 'yellow': '\x1b[5;30;43m'}.get(color, '') + text + '\x1b[0m')
def num_to_color(num) -> str:
    return 'red' if num < 0 else 'green'


def decimalize(val) -> str:
    rounded = float(int(val * 1000.0))/1000.0
    return str(rounded)

def print_line():
    print("========================================")

def headers(signature, key) -> dict:
    return {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': key
    }

def headers_epoch(signature,key,epoch) -> dict:
    return {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': key,
        'X-AUTH-EPOCH': epoch
    }
def headers_no_sign(key) -> dict:
    return {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key
    }
