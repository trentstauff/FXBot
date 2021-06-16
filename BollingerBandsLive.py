import numpy as np

from LiveTrader import LiveTrader


class BollingerBandsLive(LiveTrader):

    def __init__(self, cfg, instrument, bar_length, sma, deviation, units):
        # passes params to the parent class
        super().__init__(cfg, instrument, bar_length, units)
        self._sma = sma
        self._deviation = deviation

    def define_strategy(self):
        data = self._raw_data.copy()

        data["sma"] = data["bid_price"].rolling(self._sma).mean()
        data["lower"] = data["sma"] - (data["bid_price"].rolling(self._sma).std() * self._deviation)
        data["upper"] = data["sma"] + (data["bid_price"].rolling(self._sma).std() * self._deviation)
        data["distance"] = data["bid_price"] - data["sma"]

        # if price is lower than lower band, indicates oversold, and to go long
        data["position"] = np.where(data["bid_price"] < data["lower"], 1, np.nan)
        # if price is higher than upper band, indicates overbought, and to go short
        data["position"] = np.where(data["bid_price"] > data["upper"], -1, data["position"])
        # if we have crossed the sma line, we want to close our current position (be neutral, position=0)
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])
        # clean up any NAN values/holiday vacancies
        data["position"] = data.position.ffill().fillna(0)

        self._data = data.dropna().copy()

