from crypto import *

def main():
    c = Crypto.boot()
    c.folio()
    c.candle("btc")
    c.metrics()
   
main()