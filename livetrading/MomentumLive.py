import numpy as np

from livetrading.LiveTrader import LiveTrader


class MomentumLive(LiveTrader):
    def __init__(
        self,
        cfg,
        instrument,
        bar_length,
        window,
        units,
        stop_datetime=None,
        stop_loss=None,
        stop_profit=None,
    ):
        """
        Initializes the MomentumLive object.

        Args:
            cfg (object): An object representing the OANDA connection
            instrument (string): A string holding the ticker instrument of instrument to be tested
            bar_length (string): Length of each candlestick for the respective instrument
            window (int): Length of sliding window to consider
            units (int): Amount of units to take positions with
            stop_datetime (object) <DEFAULT = None>: A datetime object that when passed stops trading
            stop_loss (float) <DEFAULT = None>: A stop loss that when profit goes below stops trading
            stop_profit (float) <DEFAULT = None>: A stop profit that when profit goes above stops trading
        """
        self._window = window

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
        data["returns"] = np.log(data["mid_price"].div(data["mid_price"].shift(1)))
        data["position"] = np.sign(data["returns"].rolling(self._window).mean())
        self._data = data.dropna().copy()
