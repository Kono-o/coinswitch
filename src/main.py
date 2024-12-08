import coinswitch

def main():
    session = coinswitch.CS.boot()
    session.info("xrp")
    session.info("doge")
    session.candle("eth")
    session.candle("btc")
main()