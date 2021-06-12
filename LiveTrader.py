import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import time
import tpqoa


class LiveTrader(tpqoa.tpqoa):

    def __init__(self, cfg, instrument, bar_length, units, history_days=7):

        # TODO: More rigorous handling of markets being closed (this is EST dependent, must ensure that is what the datetime is giving)
        if datetime.today().weekday() > 6 and  datetime.today().hour > 17:
            print("Markets are open.")
        elif datetime.today().weekday() == 5:
            raise Exception("Sorry, markets are closed")
        elif datetime.today().weekday() >= 4 and datetime.today().hour >= 23:
            raise Exception("Sorry, markets are closed")
        else:
            print("Markets are open.")

        # passes the config file to tpqoa
        super().__init__(cfg)
        self._instrument = instrument
        self._bar_length = pd.to_timedelta(bar_length)
        self._tick_data = pd.DataFrame()
        self._raw_data = None
        self._data = None
        self._last_tick = None
        self._units = units

        self._position = 0

        # set up history used by some trades
        self.setup_history(history_days)

    # destructor
    def __del__(self):
        # close out position
        self.close_position()

    # used to gather historical data used by some strategies (such as SMA)
    def setup_history(self, days=7):
        # while loop to combat missing bar on boundary of historical and streamed data
        while True:
            time.sleep(2)
            now = datetime.utcnow()
            now = now.replace(microsecond=0)
            past = now - timedelta(days=days)
            print(now)
            bid_price = self.get_history(instrument=self._instrument, start=past, end=now, granularity="S5", price="B", localize=False).c.dropna().to_frame()
            print(bid_price)
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
            # this way we never have a missing boundary bar between historical and stream
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
            self.trade()

    def define_strategy(self):
        pass

    def trade(self):
        # if most recent bar in position of strat says to go long, do it
        if self._data["position"].iloc[-1] == 1:
            # if we were neutral, only need to go long "units"
            if self._positon == 0:
                order = self.create_order(self._instrument, self._units, suppress=True, ret=True)
            # if we were short, need to go long 2 * "units"
            elif self._position == -1:
                order = self.create_order(self._instrument, self._units * 2, suppress=True, ret=True)

            print("Going Long")
            self._position = 1

        # short position
        elif self._data["position"].iloc[-1] == -1:
            # if we were neutral, only need to go short "units"
            if self._positon == 0:
                order = self.create_order(self._instrument, -self._units, suppress=True, ret=True)
            # if we were short, need to go short 2 * "units"
            elif self._position == 1:
                order = self.create_order(self._instrument, -(self._units * 2), suppress=True, ret=True)

            print("Going Short")
            self._position = -1

        # if we want to go neutral, close out current open position
        elif self._data["position"].iloc[-1] == 0:

            if self._positon == 1:
                order = self.create_order(self._instrument, -self._units, suppress=True, ret=True)

            elif self._position == -1:
                order = self.create_order(self._instrument, self._units, suppress=True, ret=True)
            print("Going Neutral, Closing Open Position")

            self._position = 0

    def close_position(self):
        if self._position != 0:
            self.create_order(self._instrument, units = -(self._position * self._units), suppress=True, ret=True)
        self._position = 0
