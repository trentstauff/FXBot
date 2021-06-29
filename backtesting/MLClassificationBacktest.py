import numpy as np
from sklearn.linear_model import LogisticRegression

from backtesting.Backtester import Backtester


class MLClassificationBacktest(Backtester):

    """
    Class implementing the vectorized backtesting of machine learning strategies.
    In this case, Classification.
    """
    def __init__(self, instrument, start, end, granularity="D", trading_cost=0):
        """
        Initializes the MLClassificationBacktest object.

        Args:
            instrument (string): A string holding the ticker instrument of instrument to be tested
            start (string): The start date for the instrument
            end (string): The end date for the instrument
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        # low regularization
        self._model = LogisticRegression(C=1e6, max_iter=100000, multi_class="ovr")

        # passes params to the parent class
        super().__init__(
            instrument,
            start,
            end,
            granularity,
            trading_cost
        )

    def __repr__(self):
        """Custom Representation."""
        return f"MLClassificationBacktest( instrument={self._instrument}, start={self._start}, end={self._end}, granularity={self._granularity}, trading_cost={self._tc} )"

    def get_hitratio(self):
        """
        Getter function to retrieve the forward test's hit ratio.

        Returns:
            Returns the hit ratio
        """
        print(self._hitratio)
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
        self._model.fit(
            self._data_subset[self._feature_columns],
            np.sign(self._data_subset["returns"]),
        )

    def prepare_features(self, start, end):
        """
        Prepares the feature columns for training/testing.

        Args:
            start (string): The start date to prepare model on
            end (string): The end date to prepare model on
        """
        self._data_subset = self.split_data(start, end)
        feature_columns = []

        for lag in range(1, self._lags + 1):
            self._data_subset[f"lag{lag}"] = self._data_subset["returns"].shift(lag)
            feature_columns.append(f"lag{lag}")

        self._data_subset.dropna(inplace=True)

        self._feature_columns = feature_columns

    def test(self, train_ratio=0.7, lags=5):
        """
        Backtests the model and then forward tests the strategy.

        Args:
            train_ratio (float [0, 1.0]) <DEFAULT = 0.7>: Splits the dataset into backtesting set (train_ratio) and test set (1-train_ratio)
            lags (int) <DEFAULT = 5>: The number of return lags serving as model features
        """
        print(f"Testing strategy with train_ratio = {train_ratio}, lags = {lags} ...")

        self._lags = lags

        df = self._data.copy()

        # splits data
        split_index = int(len(df) * train_ratio)
        split_date = df.index[split_index - 1]
        backtest_start = df.index[0]
        test_end = df.index[-1]

        # fits the model on the backtest data
        self.fit_model(backtest_start, split_date)

        # prepares the test set
        self.prepare_features(split_date, test_end)

        # makes predictions on the test set
        self._data_subset["prediction"] = self._model.predict(
            self._data_subset[self._feature_columns]
        )

        # strat returns
        self._data_subset["strategy"] = (
            self._data_subset["prediction"] * self._data_subset["returns"]
        )

        # number of trades
        self._data_subset["trades"] = (
            self._data_subset["prediction"].diff().fillna(0).abs()
        )

        # adjust strat returns based on trading cost
        self._data_subset["strategy"] = self._data_subset["strategy"] - (
            self._data_subset["trades"] * self._tc
        )

        self._data_subset["creturns"] = (
            self._data_subset["returns"].cumsum().apply(np.exp)
        )
        self._data_subset["cstrategy"] = (
            self._data_subset["strategy"].cumsum().apply(np.exp)
        )

        self._results = self._data_subset

        # stores the number of times we are correct or wrong with the prediction
        self._hits = np.sign(
            self._data_subset.returns * self._data_subset.prediction
        ).value_counts()
        # see how often we are correct
        self._hitratio = self._hits[1.0] / sum(self._hits)

        # absolute performance of strat
        performance = self._results["cstrategy"].iloc[-1]

        # outperformance of strat vs buy and hold on interval
        out_performance = performance - self._results["creturns"].iloc[-1]

        print(f"Return: {round(performance * 100 - 100, 2)}%, Out Performance: {round(out_performance * 100, 2)}%")

        return performance, out_performance
