import coinswitch

def main():
    session = coinswitch.CS.boot()

    session.pull("xrp")
    session.pull("doge")
    session.pull("xlm")

    session.candle("eth")
    session.candle("btc")

    session.folio()
main()