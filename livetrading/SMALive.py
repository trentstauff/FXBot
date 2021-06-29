import numpy as np

from livetrading.LiveTrader import LiveTrader


class SMALive(LiveTrader):
    def __init__(
        self,
        cfg,
        instrument,
        bar_length,
        smas,
        smal,
        units,
        stop_datetime=None,
        stop_loss=None,
        stop_profit=None,
    ):
        """
        Initializes the SMALive object.

        Args:
            cfg (object): An object representing the OANDA connection
            instrument (string): A string holding the ticker instrument of instrument to be tested
            bar_length (string): Length of each candlestick for the respective instrument
            smas (int): A value for the # of days the Simple Moving Average lags (Shorter) should consider
            smal (int): A value for the # of days the Simple Moving Average lags (Longer) should consider
            stop_datetime (object) <DEFAULT = None>: A datetime object that when passed stops trading
            stop_loss (float) <DEFAULT = None>: A stop loss that when profit goes below stops trading
            stop_profit (float) <DEFAULT = None>: A stop profit that when profit goes above stops trading
        """
        # these should be in terms of minutes
        self._smas = smas
        self._smal = smal

        # passes params to the parent class
        super().__init__(
            cfg,
            instrument,
            bar_length,
            units,
            stop_datetime=stop_datetime,
            stop_loss=stop_loss,
            stop_profit=stop_profit,
        )

    def define_strategy(self):
        data = self._raw_data.copy()
        data["smas"] = data["mid_price"].rolling(self._smas).mean()
        data["smal"] = data["mid_price"].rolling(self._smal).mean()
        data["position"] = np.where(data["smas"] > data["smal"], 1, -1)

        self._data = data.dropna().copy()
