from coinswitch import *

def main():
    session = CoinSwitch.boot()
    session.ping()
    #session.folio()
    session.info("1mbabydoge")
    #session.order("buy", "BNB", 0.0080, 530)

main()