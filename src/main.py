from coinswitch import *

def main():
    session = CoinSwitch.boot()
    session.ping()
    session.folio()
    session.info("render")
    session.order("sell", "render", 1.0, 500)

main()