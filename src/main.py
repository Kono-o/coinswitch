from coinswitch import *


def main():
    session = CoinSwitch.boot()
    session.info("xrp")
    session.refresh()
    session.info("xrp")
    session.info("chillguy")

main()