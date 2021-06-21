import numpy as np

from LiveTrader import LiveTrader


class SMALive(LiveTrader):

    def __init__(self, cfg, instrument, bar_length, smas, smal, units, stop_time=None, stop_loss=None, stop_profit=None):
        # passes params to the parent class
        super().__init__(cfg, instrument, bar_length, units, stop_time=stop_time, stop_loss=stop_loss, stop_profit=stop_profit)

        # these should be in terms of minutes
        self._smas = smas
        self._smal = smal

    def define_strategy(self):
        data = self._raw_data.copy()
        data["smas"] = data["mid_price"].rolling(self._smas).mean()
        data["smal"] = data["mid_price"].rolling(self._smal).mean()
        data["position"] = np.where(data["smas"] > data["smal"], 1, -1)

        self._data = data.dropna().copy()
