from coinswitch import *

def main():
    api = CoinSwitch.boot()

    api.folio()
    api.info("eth")
    api.info("xlm")
    api.info("fakecoin")

    api.sell("eth", 1, 11)

main()