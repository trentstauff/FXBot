import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tpqoa
from sklearn.linear_model import LinearRegression

plt.style.use("seaborn")


class MultipleRegressionModelPredictor:
    """
    Attempts to predict the direction of returns.
    """
    def __init__(self, symbol, backtest_range, forwardtest_range, window=3, granularity="D", trading_cost=0):
        """

        """

        # TODO: Ensure backtest range is before forward test range (or at least warn)

        self._symbol = symbol
        self._startb = backtest_range[0]
        self._endb = backtest_range[1]
        self._startf = forwardtest_range[0]
        self._endf = forwardtest_range[1]
        self._window = window
        self._granularity = granularity
        self._tc = trading_cost

        # stores a Pandas dataframe holding the results of test() or optimize() (most recent of the two)
        self._results = None

        self.acquire_data()
        self.prepare_data()

    def acquire_data(self):
        """
        A general function to acquire data of symbol from a source.
        """
        oanda = tpqoa.tpqoa('oanda.cfg')



        backtestdf = oanda.get_history(self._symbol, self._startb, self._endb, self._granularity, "B")
        forwardtestdf = oanda.get_history(self._symbol, self._startf, self._endf, self._granularity, "B")

        # only care for the closing price
        backtestdf = backtestdf.c.to_frame()
        backtestdf.rename(columns={"c": "price"}, inplace=True)

        backtestdf.dropna(inplace=True)

        backtestdf["returns"] = np.log(backtestdf.div(backtestdf.shift(1)))

        self._backtest_df = backtestdf

        # only care for the closing price
        forwardtestdf = forwardtestdf.c.to_frame()
        forwardtestdf.rename(columns={"c": "price"}, inplace=True)

        forwardtestdf.dropna(inplace=True)

        forwardtestdf["returns"] = np.log(forwardtestdf.div(forwardtestdf.shift(1)))

        self._forwardtest_df = forwardtestdf


    def prepare_data(self):
        """
        Prepares data for strategy-specific information.

        """
        backtestdf = self._backtest_df.copy()
        forwardtestdf = self._forwardtest_df.copy()

        # now we have multiple lagging columns (depending on window length > 1)
        columns = []
        for lag in range(1, self._window+1):
            column = f"lag{lag}"
            backtestdf[column] = backtestdf.returns.shift(lag)
            forwardtestdf[column] = forwardtestdf.returns.shift(lag)
            columns.append(column)

        backtestdf.dropna(inplace=True)
        forwardtestdf.dropna(inplace=True)

        self._lm = LinearRegression(fit_intercept=True)

        # has multiple independent variables
        self._lm.fit(backtestdf[columns], backtestdf.returns)

        forwardtestdf["prediction"] = self._lm.predict(forwardtestdf[columns].values)

        # only interested in the direction of returns, not the magnitude
        forwardtestdf["prediction"] = np.sign(forwardtestdf["prediction"])

        self._forwardtest_df = forwardtestdf

        # stores the number of times we are correct or wrong with the prediction
        self._hits = np.sign(forwardtestdf.returns * forwardtestdf.prediction).value_counts()
        # see how often we are correct
        self._hitratio = self._hits[1.0] / sum(self._hits)

    def get_data(self):
        """
        Getter function to retrieve current symbol's dataframe.

        Returns:
            Returns the stored Pandas dataframe with information regarding the symbol
        """
        return self._forwardtest_df

    def get_hitratio(self):
        return self._hitratio

    def test(self):
        """

        """
        data = self._forwardtest_df.copy()

        data["strategy"] = data.prediction * data.returns

        data["trades"] = data.prediction.diff().fillna(0).abs()

        # correct strategy returns based on trading costs
        data.strategy = data.strategy - data.trades * self._tc

        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)

        self._results = data

        performance = data["cstrategy"].iloc[-1]
        # out_performance is our strats performance vs a buy and hold on the interval
        out_performance = performance - data["creturns"].iloc[-1]

        return performance, out_performance

    def plot_results(self):
        """
        Plots the results of test() or optimize().
        Also plots the results of the buy and hold strategy on the interval [start,end] to compare to the results.
        """
        if self._results is not None:
            title = f"{self._symbol} | Multiple Regression of {self._window}, Granularity of {self._granularity}, Trading Cost of {self._tc}"
            self._results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
            plt.show()
        else:
            print("Please run test() or optimize().")