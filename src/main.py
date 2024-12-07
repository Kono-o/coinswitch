from coinswitch import *

def main():
    session = CoinSwitch.boot()
    session.ping()
    session.folio()
    session.info("render")
    session.order("sell", "render", 0.0, 0.0)

main()