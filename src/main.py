from crypto import *

def main():
    c = Crypto.boot()
    c.folio()
    c.metrics()
    c.candle("btc")

main()