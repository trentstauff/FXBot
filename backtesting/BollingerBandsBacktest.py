import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tpqoa

plt.style.use("seaborn")


class BollingerBandsBacktest:
    """
    Class implementing vectorized back-testing of a Bollinger Bands trading strategy.
    """
    def __init__(self, symbol, start, end, sma=20, deviation=2, granularity="D", trading_cost=0):
        """
        Initializes the BollingerBandsBacktest object.

        Args:
            symbol (string): A string holding the ticker symbol of instrument to be tested
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            sma (int) <DEFAULT = 20>: Length of sliding average lags
            deviation (int) <DEFAULT = 2>: Standard deviation multiplier for upper and lower bands
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective symbol
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._symbol = symbol
        self._start = start
        self._end = end
        self._sma = sma
        self._deviation = deviation
        self._granularity = granularity
        self._tc = trading_cost

        # stores a Pandas dataframe holding the results of test() or optimize() (most recent of the two)
        self._results = None

        # _data stores a Pandas dataframe of general values to be used by the testing strategy
        # _data is built by acquiring data (download) followed by preparing data (strategy specific info)
        self._data = self.acquire_data()
        self._data = self.prepare_data()

    def __repr__(self):
        return f"BollingerBandsBacktest( symbol={self._symbol}, start={self._start}, end={self._end}, sma={self._sma}, deviation={self._deviation}, granularity={self._granularity}, trading_cost={self._tc}  )";

    def acquire_data(self):
        """
        A general function to acquire data of symbol from a source.

        Returns:
            Returns a Pandas dataframe containing downloaded info.
            Includes: Date, Price, and Returns (%) (on the interval [start,end])
        """
        oanda = tpqoa.tpqoa('../oanda.cfg')

        try:
            df = oanda.get_history(self._symbol, self._start, self._end, self._granularity, "B")
        except:
            raise ValueError("Please choose a supported instrument trading on OANDA, in the form XXX/YYY or XXX_YYY.")

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
            Returns a Pandas dataframe
        """
        df = self._data.copy()
        df["sma"] = df.price.rolling(self._sma).mean()

        df["lower"] = df["sma"] - (df.price.rolling(self._sma).std() * self._deviation)
        df["upper"] = df["sma"] + (df.price.rolling(self._sma).std() * self._deviation)

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

    def set_params(self, sma=None, deviation=None):
        """
        Allows the caller to reset/override the current sma value and the deviation value,
        which also updates the prepared dataset associated with the symbol.

        Args:
            sma (int): The new sma
            deviation (int): The new deviation
        """

        if sma is not None:
            self._sma = sma
            self._data["sma"] = self._data.price.rolling(self._sma).mean()

            # error with python... https://github.com/pandas-dev/pandas/issues/21786 .std() doesnt work
            self._data["lower"] = self._data["sma"] - self._data.price.rolling(self._sma).apply(lambda x: np.std(x)) * self._deviation
            self._data["upper"] = self._data["sma"] + self._data.price.rolling(self._sma).apply(lambda x: np.std(x)) * self._deviation

        if deviation is not None:
            self._deviation = deviation
            self._data["lower"] = self._data["sma"] - (self._data.price.rolling(self._sma).apply(lambda x: np.std(x)) * deviation)
            self._data["upper"] = self._data["sma"] + (self._data.price.rolling(self._sma).apply(lambda x: np.std(x)) * deviation)


    def test(self):
        """
        Executes the back-testing of the Bollinger Bands strategy on the set instrument.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """
        data = self._data.copy().dropna()

        data["distance"] = data["price"] - data["sma"]

        # if price is lower than lower band, indicates oversold, and to go long
        data["position"] = np.where(data["price"] < data["lower"], 1, np.nan)

        # if price is higher than upper band, indicates overbought, and to go short
        data["position"] = np.where(data["price"] > data["upper"], -1, data["position"])

        # if we have crossed the sma line, we want to close our current position (be neutral, position=0)
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])

        # clean up any NAN values/holiday vacancies
        data["position"] = data.position.ffill().fillna(0)

        data["strategy"] = data.position.shift(1) * data["returns"]

        data.dropna(inplace=True)

        data["trades"] = data.position.diff().fillna(0).abs()

        # correct strategy returns based on trading costs (only applicable if self._tc > 0)
        data.strategy = data.strategy - data.trades * self._tc

        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        self._results = data

        performance = data["cstrategy"].iloc[-1]
        # out_performance is our strats performance vs a buy and hold on the interval
        out_performance = performance - data["creturns"].iloc[-1]

        return performance, out_performance

    def optimize(self, sma_range=(1,252), dev_range=(1,3)):
        """
        Optimizes the sma and deviation on the interval [start,end] which allows for the greatest return.

        Returns:
            Returns a tuple, (float: max_return, int: best_sma, int: best_dev)
            -> "max_return" is the optimized (maximum) return rate of the instrument on the interval [start,end]
            -> "best_sma" is the optimized global best_sma value that maximizes return
            -> "best_dev" is the optimized global best_dev value that maximizes return
        """

        if sma_range[0] >= sma_range[1] or dev_range[0] >= dev_range[1]:
            print("The ranges must satisfy: (X,Y) -> X < Y")
            return

        max_return = float('-inf')
        best_sma = -1
        best_dev = -1
        for sma in range(sma_range[0],sma_range[1]):

            if sma == sma_range[1]/4: print("25%...")
            if sma == sma_range[1]/2: print("50%...")
            if sma == sma_range[1]/1.5: print("75%...")

            for dev in range(dev_range[0],dev_range[1]):
                self.set_params(sma, dev)
                current_return = self.test()[0]

                if current_return > max_return:
                    max_return = current_return
                    best_sma = sma
                    best_dev = dev

        self.set_params(best_sma, best_dev)
        self.test()

        return max_return, best_sma, best_dev

    def plot_results(self):
        """
        Plots the results of test() or optimize().
        Also plots the results of the buy and hold strategy on the interval [start,end] to compare to the results.
        """
        if self._results is not None:
            title = f"Bollinger Bands: {self._symbol} | sma {self._sma}, deviation {self._deviation}"
            self._results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
            plt.show()
        else:
            print("Please run test() or optimize().")
