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
        endpoints = {
            'ping': "ping",
            'time': "time",
            'portfolio': "user/portfolio",
            'info': "tradeInfo",
            'tax': "tds",
            'order': "order"
        }
        keys = util.env()
        signatures = api.sign(keys, endpoints)
        tax,year = api.tds(keys['api'], signatures['tax'], endpoints['tax'])
        portfolio = api.folio(keys['api'], signatures['portfolio'], endpoints['portfolio'], tax)
        return cls(year, keys, signatures, portfolio, endpoints)

    def ping(self):
        time = self.time()
        if api.ping(self.endpoints['ping']):
            print(time + util.link("") + " is up!")
        else:
            print(time + util.link("") + "may be down.")
        util.print_line()
    def refresh(self):
        tax, self.fiscal_year = api.tds(self.keys['api'], self.signatures['tax'], self.endpoints['tax'])
        self.portfolio = api.folio(self.keys['api'], self.signatures['portfolio'], self.endpoints['portfolio'], tax)
        print(self.time() + "portfolio has been refreshed!")

    def info(self, ticker):
        ticker = ticker.upper()
        is_valid, minim = api.info(ticker, self.keys['api'], self.endpoints['info'])
        if not is_valid:
            print(f"{ticker} not a valid token")
            return
        print("sell min: ₹", minim)
        if ticker in self.portfolio:
            print("currently in portfolio.")
            api.token_display(self.portfolio[ticker],ticker, True)
        else:
            print("not in portfolio.")
    def folio(self):
        api.folio_display(self.portfolio)
    def order(self, action, ticker, quantity, price):
        if quantity == 0 or price == 0:
            print(
                f"sending order to {action} ⦿{util.decimalize(quantity)} {ticker.upper()} for ₹{util.decimalize(price)}...")
            util.print_color("failed!", "red")
            print("not enough token or price.")
            return
        price_whole = (1.0/quantity) * price
        print(f"sending order to {action} ⦿{util.decimalize(quantity)} {ticker.upper()} for ₹{util.decimalize(price)} (₹{util.decimalize(price_whole)} per token)...")
        valid, order = api.sign_order(self.keys, self.endpoints['order'], action, ticker, price_whole, quantity)
        if valid == 0:
            util.print_color("success!", "green")
            print("order id:", order['id'])
            util.print_line()
            return
        util.print_color("failed!", "red")
        match valid:
            case 1:
                print("wrong action or token.")
            case 2:
                print("not enough token or balance.")
            case 3:
                print("too less token. (less than ₹150)")
            case 4:
                print("unexpected error.")
        util.print_line()

    def time(self) -> str:
        return api.server_time(self.endpoints['time'])