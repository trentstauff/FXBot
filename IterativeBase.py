import tpqoa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class IterativeBase:

    def __init__(self, symbol, start, end, amount, granularity="D",):
        self._symbol = symbol
        self._start = start
        self._end = end
        self._initial_balance = amount
        self._current_balance = amount
        self._granularity = granularity

        self.acquire_data()

    def acquire_data(self):
       """
       A general function to acquire data of an instrument from a source.
       """
       oanda = tpqoa.tpqoa('oanda.cfg')

       bid_df = oanda.get_history(self._symbol, self._start, self._end, self._granularity, "B")
       ask_df = oanda.get_history(self._symbol, self._start, self._end, self._granularity, "A")

       bid_price = bid_df.c.to_frame()
       ask_price = ask_df.c.to_frame()

       spread = ask_price - bid_price

       # create the new dataframe with relevent info
       df = bid_price
       df.rename(columns={"c": "bid_price"}, inplace=True)
       df["ask_price"] = ask_price
       df["spread"] = spread

       df.dropna(inplace=True)

       df["returns"] = np.log(df.bid_price.div(df.bid_price.shift(1)))
       print(df)

       self._data = df

    def bar_info(self, bar):
        date = str(self._data.index[bar].date())
        # round price to 5 as OANDA only gives 5 decimal places
        price = round(self._data.bid_price.iloc[bar],5)
        spread = round(self._data.spread.iloc[bar],5)

        return date, price, spread

    def print_current_balance(self, bar):
        date, price, spread = self.bar_info(bar)
        print(f"{date}: Current Balance={self._current_balance}")
    
    def plot_data(self, columns="bid_price"):
        self._data[columns].plot(figsize=(12,8), title=self._symbol)
        plt.show()

