import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tpqoa

plt.style.use("seaborn")


class SMABacktest:
    """
    Class implementing vectorized back-testing of a SMA trading strategy.
    """

    def __init__(self, symbol, start, end, smas, smal, granularity="D", trading_cost=0):
        """
        Initializes the SMABacktest object.

        Args:
            symbol (string): A string holding the ticker symbol of instrument to be tested
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            smas (int): A value for the # of days the Simple Moving Average lags (Shorter) should consider
            smal (int): A value for the # of days the Simple Moving Average lags (Longer) should consider
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective symbol
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._symbol = symbol
        self._start = start
        self._end = end
        self._smas = smas
        self._smal = smal
        self._granularity = granularity
        self._tc = trading_cost

        # stores a Pandas dataframe holding the results of test() or optimize() (most recent of the two)
        self._results = None

        # _data stores a Pandas dataframe of general values to be used by the testing strategy
        # _data is built by acquiring data (download) followed by preparing data (strategy specific info)
        self._data = self.acquire_data()
        self._data = self.prepare_data()

    def __repr__(self):
        return f"SMABacktest( symbol={self._symbol}, start={self._start}, end={self._end}, smas={self._smas}, smal={self._smal}, granularity={self._granularity}, trading_cost={self._tc}  )"

    def acquire_data(self):
        """
        A general function to acquire data of symbol from a source.

        Returns:
            Returns a Pandas dataframe containing downloaded info.
            Includes: Date, Price, and Returns (%) (on the interval [start,end])
        """
        oanda = tpqoa.tpqoa("../oanda.cfg")

        df = oanda.get_history(
            self._symbol, self._start, self._end, self._granularity, "B"
        )

        # only care for the closing price
        df = df.c.to_frame()
        df.rename(columns={"c": "price"}, inplace=True)

        df.dropna(inplace=True)

        df["returns"] = np.log(df.div(df.shift(1)))

        return df

    def prepare_data(self):
        """
        Prepares data for strategy-specific information.

        Returns:
            Returns a Pandas dataframe which is simply the original dataframe after acquiring symbol data
            but with the smas & smal rolling lags values for each dataframe entry added
        """
        df = self._data.copy()
        df["smas"] = df.price.rolling(self._smas).mean()
        df["smal"] = df.price.rolling(self._smal).mean()
        return df

    def get_data(self):
        """
        Getter function to retrieve current symbol's dataframe.

        Returns:
            Returns the stored Pandas dataframe with information regarding the symbol
        """
        return self._data

    def get_results(self):
        """
        Getter function to retrieve current symbol's dataframe after testing the strategy.

        Returns:
            Returns a Pandas dataframe with results from back-testing the strategy
        """
        if self._results is not None:
            return self._results
        else:
            print("Please run .test() first.")

    def set_params(self, SMAS=None, SMAL=None):
        """
        Allows the caller to reset/override the current SMA (Short and Long) values individually or together,
        which also updates the prepared dataset (rolling SMA values) associated with the symbol.

        Args:
            SMAS (int): The new shorter SMA
            SMAL (int): The new longer SMA
        """
        if SMAS is not None and SMAL is not None:
            if SMAS >= SMAL:
                print("The smas value must be smaller than the smal value.")
                return

        if SMAS is not None:
            self._smas = SMAS
            self._data["smas"] = self._data["price"].rolling(self._smas).mean()
        if SMAL is not None:
            self._smal = SMAL
            self._data["smal"] = self._data["price"].rolling(self._smal).mean()

    def test(self):
        """
        Executes the back-testing of the SMA strategy on the set instrument.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """
        data = self._data.copy()

        data["position"] = np.where(data["smas"] > data["smal"], 1, -1)
        data["strategy"] = data.position.shift(1) * data["returns"]
        data.dropna(inplace=True)

        # running total of amount of trades currently, each change of position is 2 trades, but can be improved.
        # likely can save one trade by combining closing of position and opening of opposite position into one trade
        # (ie current open position LONG 100 shares -> open postion SHORT (current open position shares + additional
        # shares)
        data["trades"] = data.position.diff().fillna(0).abs()

        # correct strategy returns based on trading costs
        data.strategy = data.strategy - data.trades * self._tc

        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        self._results = data

        performance = data["cstrategy"].iloc[-1]
        # out_performance is our strats performance vs a buy and hold on the interval
        out_performance = performance - data["creturns"].iloc[-1]

        return performance, out_performance

    def optimize(self):
        """
        Optimizes the smas and smal on the interval [start,end] which allows for the greatest return.
        This function attempts all combinations of: smas Days [10,50] & smal Days [100,252], so depending on the
        length of the interval, it can take some time to compute.

        Returns:
            Returns a tuple, (float: max_return, int: GSMAS, int: GSMAL)
            -> "max_return" is the optimized (maximum) return rate of the instrument on the interval [start,end]
            -> "GSMAS" is the optimized global smas value that maximizes return
            -> "GSMAL" is the optimized global smal value that maximizes return
        """
        print("Attempting all possibilities. This will take a while.")
        max_return = float("-inf")
        GSMAS = -1
        GSMAL = -1

        for SMAS in range(10, 50):

            if SMAS == 13:
                print("25%...")
            if SMAS == 25:
                print("50%...")
            if SMAS == 38:
                print("75%...")

            for SMAL in range(100, 252):

                self.set_params(SMAS, SMAL)
                current_return = self.test()[0]

                if current_return > max_return:
                    max_return = current_return
                    GSMAS = SMAS
                    GSMAL = SMAL

        self.set_params(GSMAS, GSMAL)
        self.test()

        return max_return, GSMAS, GSMAL

    def plot_results(self):
        """
        Plots the results of test() or optimize().
        Also plots the results of the buy and hold strategy on the interval [start,end] to compare to the results.
        """
        if self._results is not None:
            title = f"{self._symbol} | smas {self._smas}, smal {self._smal}"
            self._results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
            plt.show()
        else:
            print("Please run test() or optimize().")
