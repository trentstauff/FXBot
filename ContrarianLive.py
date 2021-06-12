import numpy as np

from LiveTrader import LiveTrader


class ContrarianLive(LiveTrader):

    def __init__(self, cfg, instrument, bar_length, window, units):
        # passes params to the parent class
        super().__init__(cfg, instrument, bar_length, units)
        self._window = window

    def define_strategy(self):
        data = self._raw_data.copy()
        data["returns"] = np.log(data["bid_price"].div(data["bid_price"].shift(1)))
        data["position"] = -np.sign(data["returns"].rolling(self._window).mean())
        self._data = data.dropna().copy()
