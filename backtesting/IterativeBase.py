import tpqoa
import numpy as np
import matplotlib.pyplot as plt


class IterativeBase:

    """Class allowing iterative backtesting functionalities"""
    def __init__(
        self, cfg, instrument, start, end, amount, granularity="D", use_spread=True
    ):
        """
        Initializes the IterativeBase object.

        Args:
            cfg (object): An object representing the OANDA connection
            instrument (string): A string holding the ticker instrument of instrument to be tested
            start (string): Length of each candlestick for the respective instrument
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            amount (int): Amount of units to take positions with
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            use_spread (bool) <DEFAULT = True>: An option to consider trading costs or to neglect them
        """
        self._cfg = cfg
        self._instrument = instrument
        self._start = start
        self._end = end
        self._initial_balance = amount
        self._current_balance = amount
        self._granularity = granularity
        self._use_spread = use_spread

        self._units = 0
        self._trades = 0
        self._position = 0

        self.acquire_data()

    def acquire_data(self):
        """A general function to acquire data of an instrument from a source."""
        oanda = tpqoa.tpqoa(self._cfg)

        bid_df = oanda.get_history(
            self._instrument, self._start, self._end, self._granularity, "B"
        )
        ask_df = oanda.get_history(
            self._instrument, self._start, self._end, self._granularity, "A"
        )

        bid_price = bid_df.c.to_frame()
        ask_price = ask_df.c.to_frame()

        spread = ask_price - bid_price

        # create the new dataframe with relevent info
        df = bid_price
        df.rename(columns={"c": "bid_price"}, inplace=True)
        df["ask_price"] = ask_price
        df["mid_price"] = ask_price - spread
        df["spread"] = spread

        df.dropna(inplace=True)

        df["returns"] = np.log(df.bid_price.div(df.bid_price.shift(1)))

        self._data = df

    def bar_info(self, bar):
        date = str(self._data.index[bar].date())
        # round price to 5 as OANDA only gives 5 decimal places
        price = round(self._data.bid_price.iloc[bar], 5)
        spread = round(self._data.spread.iloc[bar], 5)

        return date, price, spread

    def print_current_balance(self, bar):
        date = self.bar_info(bar)
        print(f"{date} | Current Balance: ${round(self._current_balance,2)}")

    def print_current_nav(self, bar):
        date, price = self.bar_info(bar)
        nav = self._current_balance + (self._units * price)
        print(f"{date} | Current NAV: ${round(nav,2)}")

    def print_current_position_value(self, bar):
        date, price = self.bar_info(bar)

        curr_value = self._units * price
        print(f"{date} | Current Position Value: ${round(curr_value,2)}")

    def buy(self, bar, units=None, amount=None):
        date, price, spread = self.bar_info(bar)

        # since price is bid price, to get ask price we add the spread
        if self._use_spread:
            price += spread

        if amount is not None:
            units = int(amount / price)

        if self._current_balance < units * price:
            print("Not enough balance.")
            return

        self._current_balance -= units * price
        self._units += units
        self._trades += 1
        print(
            f"{date} | Bought {units} units of {self._instrument} @ ${round(price,2)}/unit, total=${round(units*price,2)}"
        )

    def sell(self, bar, units=None, amount=None):
        date, price, spread = self.bar_info(bar)

        # since price is bid price, no need to adjust for spread

        if amount is not None:
            units = int(amount / price)

        self._current_balance += units * price
        self._units -= units
        self._trades += 1
        print(
            f"{date} | Sold {units} units of {self._instrument} @ ${round(price,2)}/unit, total=${round(units*price,2)}"
        )

    def close_position(self, bar):
        date, price, spread = self.bar_info(bar)
        print("=" * 50)
        print(f"Closing Position ({self._instrument}, {date})")

        if self._units > 0:
            # closing long position by selling (bid price)
            self._current_balance += self._units * price
        else:
            # closing short position by buying (ask price = bid_price + spread)
            self._current_balance -= abs(self._units * (price + spread))

        print(f"{date} | closed position of {self._units} units @ {price}")
        self._units = 0
        self._trades += 1
        performance = (
            (self._current_balance - self._initial_balance) / self._initial_balance
        ) * 100
        self.print_current_balance(bar)
        print(f"Performance %: {round(performance,2)}")
        print(f"Trades Executed: {self._trades}")
        print("=" * 50)

    def plot_data(self, columns="bid_price"):
        self._data[columns].plot(figsize=(12, 8), title=self._instrument)
        plt.show()
