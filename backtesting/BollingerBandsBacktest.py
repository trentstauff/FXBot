import numpy as np
from backtesting.Backtester import Backtester


class BollingerBandsBacktest(Backtester):

    """Class implementing vectorized back-testing of a Bollinger Bands trading strategy."""
    def __init__(
        self, instrument, start, end, sma=20, deviation=2, granularity="D", trading_cost=0
    ):
        """
        Initializes the BollingerBandsBacktest object.

        Args:
            instrument (string): A string holding the ticker instrument of instrument to be tested
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            sma (int) <DEFAULT = 20>: Length of sliding average lags
            deviation (int) <DEFAULT = 2>: Standard deviation multiplier for upper and lower bands
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._sma = sma
        self._deviation = deviation

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
        return f"BollingerBandsBacktest( instrument={self._instrument}, start={self._start}, end={self._end}, sma={self._sma}, deviation={self._deviation}, granularity={self._granularity}, trading_cost={self._tc}  )"

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

    def set_params(self, sma=None, deviation=None):
        """
        Allows the caller to reset/override the current sma value and the deviation value,
        which also updates the prepared dataset associated with the instrument.

        Args:
            sma (int): The new sma
            deviation (int): The new deviation
        """
        if sma is not None:
            self._sma = sma
            self._data["sma"] = self._data.price.rolling(self._sma).mean()

            # error with python... https://github.com/pandas-dev/pandas/issues/21786 .std() doesnt work
            self._data["lower"] = (
                self._data["sma"]
                - self._data.price.rolling(self._sma).apply(lambda x: np.std(x))
                * self._deviation
            )
            self._data["upper"] = (
                self._data["sma"]
                + self._data.price.rolling(self._sma).apply(lambda x: np.std(x))
                * self._deviation
            )

        if deviation is not None:
            self._deviation = deviation
            self._data["lower"] = self._data["sma"] - (
                self._data.price.rolling(self._sma).apply(lambda x: np.std(x))
                * deviation
            )
            self._data["upper"] = self._data["sma"] + (
                self._data.price.rolling(self._sma).apply(lambda x: np.std(x))
                * deviation
            )

    def test(self, mute=False):
        """
        Executes the back-testing of the Bollinger Bands strategy on the set instrument.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """
        if not mute:
            print(f"Testing strategy with sma = {self._sma}, deviation = {self._deviation} ...")

        data = self._data.copy().dropna()

        data["distance"] = data["price"] - data["sma"]

        # if price is lower than lower band, indicates oversold, and to go long
        data["position"] = np.where(data["price"] < data["lower"], 1, np.nan)

        # if price is higher than upper band, indicates overbought, and to go short
        data["position"] = np.where(data["price"] > data["upper"], -1, data["position"])

        # if we have crossed the sma line, we want to close our current position (be neutral, position=0)
        data["position"] = np.where(
            data["distance"] * data["distance"].shift(1) < 0, 0, data["position"]
        )

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

        if not mute:
            print(f"Return: {round(performance*100 - 100,2)}%, Out Performance: {round(out_performance*100,2)}%")

        return performance, out_performance

    def optimize(self, sma_range=(1, 252), dev_range=(1, 3)):
        """
        Optimizes the sma and deviation on the interval [start,end] which allows for the greatest return.

        Returns:
            Returns a tuple, (float: max_return, int: best_sma, int: best_dev)
            -> "max_return" is the optimized (maximum) return rate of the instrument on the interval [start,end]
            -> "best_sma" is the optimized global best_sma value that maximizes return
            -> "best_dev" is the optimized global best_dev value that maximizes return
        """
        ###############################################
        print("Warning: There is a current issue that will cause this optimization to take a long time.")
        ###############################################

        if sma_range[0] >= sma_range[1] or dev_range[0] >= dev_range[1]:
            print("The ranges must satisfy: (X,Y) -> X < Y")
            return

        print("Optimizing strategy...")

        max_return = float("-inf")
        best_sma = -1
        best_dev = -1
        for sma in range(sma_range[0], sma_range[1]):

            if sma == sma_range[1] / 4:
                print("25%...")
            if sma == sma_range[1] / 2:
                print("50%...")
            if sma == sma_range[1] / 1.5:
                print("75%...")

            for dev in range(dev_range[0], dev_range[1]):
                self.set_params(sma, dev)
                current_return = self.test(mute=True)[0]

                if current_return > max_return:
                    max_return = current_return
                    best_sma = sma
                    best_dev = dev

        self.set_params(best_sma, best_dev)
        self.test(mute=True)

        print(f"Strategy optimized on interval {self._start} - {self._end}")
        print(f"Max Return: {round(max_return * 100 - 100, 2) - 100}%, Best SMA: {best_sma} ({self._granularity}), Best Deviation: {best_dev}")

        return max_return, best_sma, best_dev

