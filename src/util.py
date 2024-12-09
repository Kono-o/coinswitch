import os, tzlocal
from datetime import datetime
from dotenv import load_dotenv

def env():
    load_dotenv()
    return {
            'api': os.getenv("API"),
            'secret': os.getenv("SECRET"),
            'cmc': os.getenv("CMC")
        }

def link(end) -> str:
    return "https://coinswitch.co/trade/api/v2/" +  end

def print_line():
    print_color("", "white")
def print_color(text, color):
    print(colorize(text, color))
def colorize(text, color) -> str:
    colors = {
        #darker
        'dark_black': '\x1b[0;30m',
        'dark_red': '\x1b[0;31m',
        'dark_green': '\x1b[0;32m',
        'dark_yellow': '\x1b[0;33m',
        'dark_blue': '\x1b[0;34m',
        'dark_magenta': '\x1b[0;35m',
        'dark_cyan': '\x1b[0;36m',
        'dark_white': '\x1b[0;37m',
        #brighter
        'black': '\x1b[90m',
        'red': '\x1b[91m',
        'green': '\x1b[92m',
        'yellow': '\x1b[93m',
        'blue': '\x1b[94m',
        'magenta': '\x1b[95m',
        'cyan': '\x1b[96m',
        'white': '\x1b[97m',
        #thicker
        'bold_black': '\x1b[1;90m',
        'bold_red': '\x1b[1;91m',
        'bold_green': '\x1b[1;92m',
        'bold_yellow': '\x1b[1;93m',
        'bold_blue': '\x1b[1;94m',
        'bold_magenta': '\x1b[1;95m',
        'bold_cyan': '\x1b[1;96m',
        'bold_white': '\x1b[1;97m',
        #inverted
        'bg_black': '\x1b[0;30;40m',
        'bg_red': '\x1b[0;30;41m',
        'bg_green': '\x1b[0;30;42m',
        'bg_yellow': '\x1b[0;30;43m',
        'bg_blue': '\x1b[0;30;44m',
        'bg_magenta': '\x1b[0;30;45m',
        'bg_cyan': '\x1b[0;30;46m',
        'bg_white': '\x1b[0;30;47m',
        #inverted thick
        'bold_bg_black': '\x1b[1;30;40m',
        'bold_bg_red': '\x1b[1;30;41m',
        'bold_bg_green': '\x1b[1;30;42m',
        'bold_bg_yellow': '\x1b[1;30;43m',
        'bold_bg_blue': '\x1b[1;30;44m',
        'bold_bg_magenta': '\x1b[1;30;45m',
        'bold_bg_cyan': '\x1b[1;30;46m',
        'bold_bg_white': '\x1b[1;30;47m',
        #underlined thick
        'bold_under_black': '\x1b[1;4;30m',
        'bold_under_red': '\x1b[1;4;31m',
        'bold_under_green': '\x1b[1;4;32m',
        'bold_under_yellow': '\x1b[1;4;33m',
        'bold_under_blue': '\x1b[1;4;34m',
        'bold_under_magenta': '\x1b[1;4;35m',
        'bold_under_cyan': '\x1b[1;4;36m',
        'bold_under_white': '\x1b[1;4;37m',
    }
    return colors.get(color, '') + text + '\x1b[0m'
def num_to_color(num) -> str:
    return 'bold_red' if num < 0 else 'bold_green'
def num_to_color_dark(num) -> str:
    return 'dark_red' if num < 0 else 'dark_green'
def num_to_color_bg(num) -> str:
    return 'bold_bg_red' if num < 0 else 'bold_bg_green'
def num_to_greed(num) -> str:
    if num <= 33:
        return "bold_red"
    if num <= 66:
        return "bold_yellow"
    else:
        return "bold_green"

def num_format_huge(val) -> str:
    if val >= 1e12:
        return f"{val / 1e12:.2f}T"
    if val >= 1e9:
        return f"{val / 1e9:.2f}B"
    return num_format(val)

def ten_pow(x):
    return pow(10,x)

def num_format(val) -> str:
    tens = ten_pow(2)
    return str(float(int(val * tens))/tens)

def token_format(val) -> str:
    tens = ten_pow(5)
    return str(float(int(val * tens)) / tens)

def chronify(timestamp):
    timestamp = timestamp / 1000
    return "[" + datetime.fromtimestamp(timestamp, tzlocal.get_localzone()).strftime("%Y-%m-%d at %H:%M:%S") + "] "

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
