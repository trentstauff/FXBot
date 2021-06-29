import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from datetime import datetime, timedelta

from livetrading.LiveTrader import LiveTrader
import tpqoa


class MLClassificationLive(LiveTrader):
    def __init__(
        self,
        cfg,
        instrument,
        bar_length,
        lags,
        units,
        history_days=7,
        stop_datetime=None,
        stop_loss=None,
        stop_profit=None,
    ):
        """
        Initializes the MLClassificationLive object.

        Args:
            cfg (object): An object representing the OANDA connection
            instrument (string): A string holding the ticker instrument of instrument to be tested
            bar_length (string): Length of each candlestick for the respective instrument
            lags (int): Amount of lagged returns to consider
            units (int): Amount of units to take positions with
            history_days (int) <DEFAULT = 7>: Amount of prior days to train the model on
            stop_datetime (object) <DEFAULT = None>: A datetime object that when passed stops trading
            stop_loss (float) <DEFAULT = None>: A stop loss that when profit goes below stops trading
            stop_profit (float) <DEFAULT = None>: A stop profit that when profit goes above stops trading
        """
        # some of this info is needed by fit_model(), so we must set it in the child class
        self._instrument = instrument
        self._bar_length = pd.to_timedelta(bar_length)
        self._lags = lags
        self._model = None
        self.fit_model()

        # passes params to the parent class
        super().__init__(
            cfg,
            instrument,
            bar_length,
            units,
            history_days,
            stop_datetime=stop_datetime,
            stop_loss=stop_loss,
            stop_profit=stop_profit,
        )

    def fit_model(self):
        print("Fitting model on past 7 days...")
        now = datetime.utcnow()
        now = now.replace(microsecond=0)
        past = now - timedelta(days=7)

        oanda = tpqoa.tpqoa("oanda.cfg")

        mid_price = oanda.get_history(instrument=self._instrument, start=past, end=now, granularity="S5", price="M", localize=False).c.dropna().to_frame()

        data = mid_price
        data.rename(columns={"c": "mid_price"}, inplace=True)

        data = data.resample(self._bar_length, label="right").last().dropna().iloc[:-1]

        data["returns"] = np.log(data.div(data.shift(1)))
        data.dropna(inplace=True)

        data["direction"] = np.sign(data["returns"])

        pd.set_option("max_columns", None)

        feature_columns = []

        for lag in range(1, self._lags + 1):
            data[f"lag{lag}"] = data["returns"].shift(lag)
            feature_columns.append(f"lag{lag}")

        data.dropna(inplace=True)

        model = LogisticRegression(C=1e6, max_iter=100000, multi_class="ovr")
        model.fit(data[feature_columns], data["direction"])

        self._model = model

        data["pred"] = self._model.predict(data[feature_columns])

        print("Model fitted.")

    def define_strategy(self):
        data = self._raw_data.copy()

        data = data.append(self._tick_data.iloc[-1])
        data["returns"] = np.log(data["mid_price"] / data["mid_price"].shift())

        feature_columns = []

        for lag in range(1, self._lags + 1):
            data[f"lag{lag}"] = data["returns"].shift(lag)
            feature_columns.append(f"lag{lag}")

        data.dropna(inplace=True)

        # use the passed model to predict our positions
        data["position"] = self._model.predict(data[feature_columns])

        self._data = data.dropna().copy()
