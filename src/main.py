from coinswitch import *

def main():
    session = CoinSwitch.boot()

    session.folio()
    session.info("xrp")
    session.info("xlm")
    session.info("fake-coin")
    session.refresh()

    session.sell("eth", 0.5, 500000)
    session.buy("render", 10.2, 1000000)

main()