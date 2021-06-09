import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import time
import tpqoa


class LiveTrader(tpqoa.tpqoa):

    def __init__(self, cfg, instrument, bar_length):
        # passes the config file to tpqoa
        super().__init__(cfg)
        self._instrument = instrument
        self._bar_length = pd.to_timedelta(bar_length)
        self._tick_data = pd.DataFrame()
        self._raw_data = None
        self._data = None
        self._last_tick = None

    # used to gather historical data used by some strategies (such as SMA)
    def setup_history(self, days=7):
        # while loop to combat missing bar on boundary of historical and streamed data
        while True:

            time.sleep(2)
            now = datetime.utcnow()
            now = now.replace(microsecond=0)
            past = now - timedelta(days=days)

            bid_price = self.get_history(instrument=self._instrument, start=past, end=now, granularity="S5", price="B", localize=False).c.dropna().to_frame()
            ask_price = self.get_history(instrument=self._instrument, start=past, end=now, granularity="S5", price="A", localize=False).c.dropna().to_frame()

            spread = ask_price - bid_price

            # create the new dataframe with relevent info
            df = bid_price
            df.rename(columns={"c": "bid_price"}, inplace=True)
            df["ask_price"] = ask_price
            df["mid_price"] = ask_price - spread

            df["spread"] = spread

            df = df.resample(self._bar_length, label="right").last().dropna().iloc[:-1]

            self._raw_data = df.copy()
            self._last_tick = self._raw_data.index[-1]

            # set the data if less than _bar_length time as elapsed since the last full historical bar
            # this way we never have a missing boundary bar between historical and stream data
            if (pd.to_datetime(datetime.utcnow()).tz_localize("UTC") - self._last_tick) < self._bar_length:
                break

    # called when new streamed data is successful
    def on_success(self, time, bid, ask):
        print(time, bid, ask)

        recent_tick = pd.to_datetime(time)

        df = pd.DataFrame({"bid_price": bid, "ask_price": ask, "mid_price": (ask+bid)/2, "spread": ask-bid}, index=[recent_tick])
        self._tick_data = self._tick_data.append(df)

        # resamples the tick data (if applicable), while also dropping
        # the last row (as it can be far off the resampled granularity)
        if (recent_tick - self._last_tick) >= self._bar_length:

            # append the most recent resampled ticks to self._data
            self._raw_data = self._raw_data.append(self._tick_data.resample(self._bar_length, label="right").last().ffill().iloc[:-1])

            # only keep the last tick bar (which is a pandas DataFrame)
            self._tick_data = self._tick_data.iloc[-1:]
            self._last_tick = self._raw_data.index[-1]
            self.define_strategy()

    def define_strategy(self):
        pass
