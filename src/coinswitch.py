from dataclasses import dataclass

import api
import util

@dataclass
class CoinSwitch:
    fiscal_year: str
    keys: dict
    signatures: dict
    portfolio: dict
    endpoints: dict

    @classmethod
    def boot(cls):
        api_call = "-> api.boot -> "
        util.print_color(api_call, "bold_bg_blue")
        endpoints = {
            'ping': "ping",
            'time': "time",
            'portfolio': "user/portfolio",
            'info': "tradeInfo",
            'tax': "tds",
            'order': "order"
        }
        util.print_color("fetching keys...", "bold_blue")
        keys = util.env()
        signatures = api.sign(keys, endpoints)
        util.print_color("generating signatures...", "bold_blue")
        tax,year = api.tds(keys['api'], signatures['tax'], endpoints['tax'])
        util.print_color("refreshing portfolio...", "bold_blue")
        portfolio = api.folio(keys['api'], signatures['portfolio'], endpoints['portfolio'], tax)
        util.print_color("success!", "bold_bg_green")
        util.print_line()
        return cls(year, keys, signatures, portfolio, endpoints)

    def ping(self):
        link = "[https://coinswitch.co/trade/api]"
        api_call = "-> api.ping -> "
        time = self.time()
        if api.ping(self.endpoints['ping']):
            util.print_color(api_call + time, "bold_bg_blue")
            util.print_color(link + " is up!", "bold_blue")
        else:
            util.print_color(api_call + time, "bold_bg_red")
            util.print_color(link + " may be down.", "bold_red")
        util.print_line()
    def refresh(self):
        tax, self.fiscal_year = api.tds(self.keys['api'], self.signatures['tax'], self.endpoints['tax'])
        self.portfolio = api.folio(self.keys['api'], self.signatures['portfolio'], self.endpoints['portfolio'], tax)
        print(self.time() + "portfolio has been refreshed!")

    def info(self, ticker) -> {bool, dict}:
        ticker = ticker.upper()
        api_call = "-> api.info -> "
        time = self.time()
        util.print_color( api_call + time, "bold_bg_blue")
        util.print_color(f"fetching info on ${ticker}...", "bold_blue")
        is_valid, minim = api.info(ticker, self.keys['api'], self.endpoints['info'])
        if not is_valid:
            util.print_color(f"${ticker} not a valid token", "bold_red")
            util.print_line()
            return False, {}
        if ticker in self.portfolio:
            util.print_color("currently in portfolio.", "bold_yellow")
            token = self.portfolio[ticker]
            api.token_display(token,ticker, True)
            return True, token
        else:
            util.print_color("not in portfolio.", "bold_yellow")
        print(f"sell min: ₹{minim}",)
        util.print_line()
        return False, {}
    def folio(self):
        api_call = "-> api.portfolio -> "
        time = self.time()
        util.print_color(api_call + time, "bold_bg_blue")
        util.print_color("fetching portfolio...", "bold_blue")
        api.folio_display(self.portfolio)

    def order(self, action, ticker, quantity, price):
        if quantity == 0 or price == 0:
            print(
                f"sending order to {action} ⦿{util.decimalize(quantity)} {ticker.upper()} for ₹{util.decimalize(price)}...")
            util.print_color("failed!", "red")
            print("not enough token or price.")
            return
        price_whole = (1.0/quantity) * price
        api_call = f"-> api.order.{action} -> "
        time = self.time()
        ticker_upper = ticker.upper()
        util.print_color(api_call + time, "bold_bg_blue")
        util.print_color(f"{action} order: ⦿{util.decimalize(quantity)} {ticker_upper} for ₹{util.decimalize(price)} (₹{util.decimalize(price_whole)} per token)", "bold_blue")
        valid, order = api.sign_order(self.keys, self.endpoints['order'], action, ticker, price_whole, quantity)
        if valid == 0:
            util.print_color("success!", "bold_bg_green")
            print("order id:", order['id'])
            util.print_line()
            return
        util.print_color("failed!", "bold_bg_red")
        color = "bold_red"
        match valid:
            case 1:
                util.print_color(f"${ticker_upper} not a valid token.", color)
            case 2:
                util.print_color("not enough token or balance.", color)
            case 3:
                util.print_color("too less token. (less than ₹150)", color)
            case 4:
                util.print_color("unexpected error.", color)
        util.print_line()
    def buy(self, ticker, quantity, price):
        self.order("buy", ticker, quantity, price)
    def sell(self, ticker, quantity, price):
        self.order("sell", ticker, quantity, price)

    def time(self) -> str:
        return api.server_time(self.endpoints['time'])