from coinswitch import *

def main():
    cs = CoinSwitch.boot()
    cs.ping()

    cs.info("render")
    cs.order("sell", "render", 0.2, 500)
    cs.order("sell", "render", 0.001, 500)
    cs.order("sell", "eth", 0.2, 5000)
    cs.order("sell", "fakecoin", 5, 500)

main()