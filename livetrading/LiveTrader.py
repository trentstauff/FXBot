import pandas as pd
from datetime import datetime, timedelta

import pytz

import tpqoa
import matplotlib.pyplot as plt

plt.style.use("seaborn")


class LiveTrader(tpqoa.tpqoa):
    def __init__(
        self,
        cfg,
        instrument,
        bar_length,
        units,
        history_days=1,
        stop_datetime=None,
        stop_loss=None,
        stop_profit=None,
    ):
        """
        Initializes the LiveTrader object.

        Args:
            cfg (object): An object representing the OANDA connection
            instrument (string): A string holding the ticker instrument of instrument to be tested
            bar_length (string): Length of each candlestick for the respective instrument
            units (int): Amount of units to take positions with
            history_days (int): Amount of prior days history to download
            stop_datetime (object) <DEFAULT = None>: A datetime object that when passed stops trading
            stop_loss (float) <DEFAULT = None>: A stop loss that when profit goes below stops trading
            stop_profit (float) <DEFAULT = None>: A stop profit that when profit goes above stops trading
        """
        # TODO: More rigorous handling of markets being closed (this is EST dependent, must ensure that is what the datetime is giving)
        if datetime.today().weekday() >= 6 and datetime.today().hour >= 17:
            print("Markets are open.")
        elif datetime.today().weekday() == 6 and datetime.today().hour < 17:
            raise Exception("Sorry, markets are closed")
        elif datetime.today().weekday() == 5:
            raise Exception("Sorry, markets are closed")
        elif datetime.today().weekday() >= 4 and datetime.today().hour >= 5:
            raise Exception("Sorry, markets are closed")
        else:
            print("Markets are open, beginning trading session.")

        # passes the config file to tpqoa
        super().__init__(cfg)
        self._instrument = instrument
        self._bar_length = pd.to_timedelta(bar_length)
        self._tick_data = pd.DataFrame()
        self._raw_data = None
        self._data = None
        self._last_tick = None
        self._units = units

        if stop_datetime:
            utc_datetime = stop_datetime.astimezone(pytz.utc)

            self._stop_datetime = utc_datetime
        else:
            self._stop_datetime = None

        self._stop_loss = stop_loss
        self._stop_profit = stop_profit

        self._position = 0

        self._profits = []
        self._profit = 0

        # set up history used by some trades
        self.setup_history(history_days)

        self.stream_data(self._instrument)

    def __del__(self):
        """Destructor used to ensure closing of position when object expires."""
        # close out position
        self.close_position()

    # used to gather historical data used by some strategies
    def setup_history(self, days=1):
        print("Setting up history...")
        if days != 0:
            # while loop to combat missing bar on boundary of historical and streamed data
            while True:

                now = datetime.utcnow()
                now = now.replace(microsecond=0)
                past = now - timedelta(days=days)

                mid_price = (
                    self.get_history(
                        instrument=self._instrument,
                        start=past,
                        end=now,
                        granularity="S5",
                        price="M",
                        localize=False,
                    )
                    .c.dropna()
                    .to_frame()
                )

                df = mid_price
                df.rename(columns={"c": "mid_price"}, inplace=True)

                df = (
                    df.resample(self._bar_length, label="right")
                    .last()
                    .dropna()
                    .iloc[:-1]
                )

                # uncomment if we need ask,bid,spread pricings
                # bid_price = self.get_history(instrument=self._instrument, start=past, end=now, granularity="S5", price="B", localize=False).c.dropna().to_frame()
                # ask_price = self.get_history(instrument=self._instrument, start=past, end=now, granularity="S5", price="A", localize=False).c.dropna().to_frame()
                # spread = ask_price - bid_price
                # create the new dataframe with relevent info
                # df = bid_price
                # df.rename(columns={"c": "bid_price"}, inplace=True)
                # df["ask_price"] = ask_price
                # df["mid_price"] = ask_price - spread
                # df["spread"] = spread
                # df = df.resample(self._bar_length, label="right").last().dropna().iloc[:-1]

                self._raw_data = df.copy()
                self._last_tick = self._raw_data.index[-1]

                # set the data if less than _bar_length time as elapsed since the last full historical bar
                # this way we never have a missing boundary bar between historical and stream
                if (
                    pd.to_datetime(datetime.utcnow()).tz_localize("UTC")
                    - self._last_tick
                ) < self._bar_length:
                    print("History set up. Opening trading stream.")
                    break

    # called when new streamed data is successful
    def on_success(self, time, bid, ask):
        print(time, bid, ask)

        recent_tick = pd.to_datetime(time)

        stopped = False

        if self._stop_datetime:
            if recent_tick >= self._stop_datetime:
                self.stop_stream = True
                self.close_position()
                stopped = True

        if self._stop_loss:
            if self._profit < self._stop_loss:
                self.stop_stream = True
                self.close_position()
                stopped = True

        if self._stop_profit:
            if self._profit > self._stop_profit:
                self.stop_stream = True
                self.close_position()
                stopped = True

        if stopped:
            print("Stop triggered, ending stream.")

        if not stopped:
            df = pd.DataFrame(
                {
                    "bid_price": bid,
                    "ask_price": ask,
                    "mid_price": (ask + bid) / 2,
                    "spread": ask - bid,
                },
                index=[recent_tick],
            )
            self._tick_data = self._tick_data.append(df)
            # resamples the tick data (if applicable), while also dropping
            # the last row (as it can be far off the resampled granularity)
            if (recent_tick - self._last_tick) >= self._bar_length:

                # append the most recent resampled ticks to self._data
                self._raw_data = self._raw_data.append(
                    self._tick_data.resample(self._bar_length, label="right")
                    .last()
                    .ffill()
                    .iloc[:-1]
                )

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
            if self._position == 0:
                order = self.create_order(
                    self._instrument, self._units, suppress=True, ret=True
                )
                self.trade_report(order, 1)
            # if we were short, need to go long 2 * "units"
            elif self._position == -1:
                order = self.create_order(
                    self._instrument, self._units * 2, suppress=True, ret=True
                )
                self.trade_report(order, 1)

            self._position = 1

        # short position
        elif self._data["position"].iloc[-1] == -1:
            # if we were neutral, only need to go short "units"
            if self._position == 0:
                order = self.create_order(
                    self._instrument, -self._units, suppress=True, ret=True
                )
                self.trade_report(order, -1)
            # if we were short, need to go short 2 * "units"
            elif self._position == 1:
                order = self.create_order(
                    self._instrument, -(self._units * 2), suppress=True, ret=True
                )
                self.trade_report(order, -1)

            self._position = -1

        # if we want to go neutral, close out current open position
        elif self._data["position"].iloc[-1] == 0:

            if self._position == 1:
                order = self.create_order(
                    self._instrument, -self._units, suppress=True, ret=True
                )
                self.trade_report(order, 0)

            elif self._position == -1:
                order = self.create_order(
                    self._instrument, self._units, suppress=True, ret=True
                )
                self.trade_report(order, 0)

            self._position = 0

    def close_position(self):
        if self._position != 0:
            order = self.create_order(
                self._instrument,
                units=-(self._position * self._units),
                suppress=True,
                ret=True,
            )
            self.trade_report(order, 0)
        self._position = 0

    def trade_report(self, order, position):

        time = order["time"]
        units = order["units"]
        price = order["price"]
        profit = float(order["pl"])

        self._profits.append(profit)

        cum_profits = sum(self._profits)
        self._profit = cum_profits

        print(
            f"{time} : {position} --- {units} units, price of ${price}, profit of ${profit}, cum profit of ${cum_profits}"
        )
