import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tpqoa
from sklearn.linear_model import LogisticRegression

plt.style.use("seaborn")


class MLClassificationBacktest:
    """
    Class implementing the vectorized backtesting of machine learning strategies.
    In this case, Classification.
    """
    def __init__(self, symbol, start, end, granularity="D", trading_cost=0):
        """
            Initializes the MLClassificationBacktest object.

            Args:
                symbol (string): A string holding the ticker symbol of instrument to be tested
                start (string): The start date for the instrument
                end (string): The end date for the instrument
                granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective symbol
                trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._symbol = symbol
        self._start = start
        self._end = end
        self._granularity = granularity
        self._tc = trading_cost

        # low regularization
        self._model = LogisticRegression(C=1e6, max_iter=100000, multi_class="ovr")
        self._results = None

        self._data = self.acquire_data()

    def __repr__(self):
        return f"MLClassificationBacktest( symbol={self._symbol}, start={self._start}, end={self._end}, granularity={self._granularity}, trading_cost={self._tc} )";

    def acquire_data(self):
       """
       A general function to acquire data of symbol from a source.

       Returns:
           Returns a Pandas dataframe containing downloaded info.
       """
       oanda = tpqoa.tpqoa('../oanda.cfg')

       df = oanda.get_history(self._symbol, self._start, self._end, self._granularity, "B")

       # only care for the closing price
       df = df.c.to_frame()
       df.rename(columns={"c": "price"}, inplace=True)

       df.dropna(inplace=True)

       df["returns"] = np.log(df.div(df.shift(1)))

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
        Getter function to retrieve current instrument's dataframe after testing the strategy.

        Returns:
            Returns a Pandas dataframe with results from back-testing the strategy
        """
        if self._results is not None:
            return self._results
        else:
            print("Please run .test() first.")

    def get_hitratio(self):
        """
        Getter function to retrieve the forward test's hit ratio.

        Returns:
            Returns the hit ratio
        """
        return self._hitratio

    def split_data(self, start, end):
        """
        Splits the full data into a subset of itself.

        Args:
            start (string): The start date of split
            end (string): The end date of split
        """
        return self._data.loc[start:end].copy()

    def fit_model(self, start, end):
        """
        Fits the ML model based on the training set.

        Args:
            start (string): The start date to fit model on
            end (string): The end date to fit model on
        """
        self.prepare_features(start, end)
        self._model.fit(self._data_subset[self._feature_columns], np.sign(self._data_subset["returns"]))

    def prepare_features(self, start, end):
        """
        Prepares the feature columns for training/testing.

        Args:
            start (string): The start date to prepare model on
            end (string): The end date to prepare model on
        """
        self._data_subset = self.split_data(start, end)
        feature_columns = []

        for lag in range(1, self._lags+1):
            self._data_subset[f"lag{lag}"] = self._data_subset["returns"].shift(lag)
            feature_columns.append(f"lag{lag}")

        self._data_subset.dropna(inplace=True)

        self._feature_columns = feature_columns

    def test(self, train_ratio=0.7, lags=5):
        """
        Backtests the strategy.

        Args:
            train_ratio (float [0, 1.0]) <DEFAULT = 0.7>: Splits the dataset into backtesting set (train_ratio) and test set (1-train_ratio)
            lags (int) <DEFAULT = 5>: The number of return lags serving as model features
        """
        self._lags = lags

        df = self._data.copy()

        # splits data
        split_index = int(len(df) * train_ratio)
        split_date = df.index[split_index-1]
        backtest_start = df.index[0]
        test_end = df.index[-1]

        # fits the model on the backtest data
        self.fit_model(backtest_start, split_date)

        # prepares the test set
        self.prepare_features(split_date, test_end)

        # makes predictions on the test set
        self._data_subset["prediction"] = self._model.predict(self._data_subset[self._feature_columns])

        # strat returns
        self._data_subset["strategy"] = self._data_subset["prediction"] * self._data_subset["returns"]

        # number of trades
        self._data_subset["trades"] = self._data_subset["prediction"].diff().fillna(0).abs()

        # adjust strat returns based on trading cost
        self._data_subset["strategy"] = self._data_subset["strategy"] - (self._data_subset["trades"] * self._tc)

        self._data_subset["creturns"] = self._data_subset["returns"].cumsum().apply(np.exp)
        self._data_subset["cstrategy"] = self._data_subset["strategy"].cumsum().apply(np.exp)

        self._results = self._data_subset

        # stores the number of times we are correct or wrong with the prediction
        self._hits = np.sign(self._data_subset.returns * self._data_subset.prediction).value_counts()
        # see how often we are correct
        self._hitratio = self._hits[1.0] / sum(self._hits)

        # absolute performance of strat
        performance = self._results["cstrategy"].iloc[-1]

        # outperformance of strat vs buy and hold on interval
        out_performance = performance - self._results["creturns"].iloc[-1]

        return performance, out_performance

    def plot_results(self):
        """
        Plots the results of test().
        Also plots the results of the buy and hold strategy on the interval [start,end] to compare to the results.
        """
        if self._results is not None:
            title = f"{self._symbol} | Logistic Regression: Lags={self._lags}, Granularity={self._granularity}, Trading Cost={self._tc}"
            self._results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
            plt.show()
        else:
            print("Please run test().")
