from LiveTrader import LiveTrader

class BollingerBandsLive(LiveTrader):

    def __init__(self, cfg, instrument, bar_length):
        # passes params to the parent class
        super().__init__(cfg, instrument, bar_length)

    def define_strategy(self):
        pass
