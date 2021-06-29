import numpy as np
import tpqoa
from sklearn.linear_model import LinearRegression

from backtesting.Backtester import Backtester


class MultipleRegressionModelPredictor(Backtester):

    """
    Predicts the direction of returns for each granularity time stamp, by fitting to a known time range
    and then predicting a future time range.
    """
    def __init__(self, instrument, backtest_range, forwardtest_range, lags=3, granularity="D", trading_cost=0):
        """
        Initializes the MultipleRegressionModelPredictor object.

        Args:
            instrument (string): A string holding the ticker instrument of instrument to be tested
            backtest_range (tuple: str): The date range of the backtesting testing period
            forwardtest_range (tuple: str): The date range of period to predict
            lags (int): Number of lags to consider when fitting
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """

        if backtest_range[0] > backtest_range[1] or forwardtest_range[0] > forwardtest_range[1] or backtest_range[1] > forwardtest_range[0]:
            raise ValueError("Please ensure that the start date for each date range is earlier than the end date, and also ensure the backtest range is completely before the forwardtest range.")

        self._startb = backtest_range[0]
        self._endb = backtest_range[1]
        self._startf = forwardtest_range[0]
        self._endf = forwardtest_range[1]
        self._lags = lags

        # passes params to the parent class
        super().__init__(
            instrument,
            forwardtest_range[0],
            forwardtest_range[1],
            granularity,
            trading_cost
        )

    def acquire_data(self):
        """
        Sets up the backtest data as well as the forward test data
        """
        oanda = tpqoa.tpqoa('oanda.cfg')

        # get data of both periods
        backtestdf = oanda.get_history(self._instrument, self._startb, self._endb, self._granularity, "M")
        forwardtestdf = oanda.get_history(self._instrument, self._startf, self._endf, self._granularity, "M")

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

        # we have multiple lagging columns (depending on lags length > 1)
        columns = []
        for lag in range(1, self._lags + 1):
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

    def get_hitratio(self):
        """
        Getter function to retrieve the forward test's hit ratio.

        Returns:
            Returns the hit ratio
        """
        print(self._hitratio)
        return self._hitratio

    def test(self):
        """
        Computes the strategies returns over the forwardtest interval.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """
        print("Testing strategy...")

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

        print(f"Return: {round(performance * 100 - 100, 2)}%, Out Performance: {round(out_performance * 100, 2)}%")

        return performance, out_performance
