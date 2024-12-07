from coinswitch import *

def main():
    cs = CoinSwitch.boot()
    cs.ping()

    cs.show_folio()
    cs.info("eth")
    cs.info("render")



main()