import numpy as np

from backtesting.Backtester import Backtester


class SMABacktest(Backtester):
    """Class implementing vectorized back-testing of a SMA Cross trading strategy."""
    def __init__(self, instrument, start, end, smas, smal, granularity="D", trading_cost=0):
        """
        Initializes the SMABacktest object.

        Args:
            instrument (string): A string holding the ticker instrument of instrument to be tested
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            smas (int): A value for the # of days the Simple Moving Average lags (Shorter) should consider
            smal (int): A value for the # of days the Simple Moving Average lags (Longer) should consider
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._smas = smas
        self._smal = smal

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
        return f"SMABacktest( instrument={self._instrument}, start={self._start}, end={self._end}, smas={self._smas}, smal={self._smal}, granularity={self._granularity}, trading_cost={self._tc}  )"

    def prepare_data(self):
        """
        Prepares data for strategy-specific information.

        Returns:
            Returns a Pandas dataframe which is simply the original dataframe after acquiring instrument data
            but with the smas & smal rolling lags values for each dataframe entry added
        """
        df = self._data.copy()
        df["smas"] = df.price.rolling(self._smas).mean()
        df["smal"] = df.price.rolling(self._smal).mean()
        return df

    def set_params(self, SMAS=None, SMAL=None):
        """
        Allows the caller to reset/override the current SMA (Short and Long) values individually or together,
        which also updates the prepared dataset (rolling SMA values) associated with the instrument.

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

    def test(self, mute=False):
        """
        Executes the back-testing of the SMA Cross strategy on the set instrument.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """

        if not mute:
            print(f"Testing strategy with smas = {self._smas}, smal = {self._smal} ...")

        data = self._data.copy()

        data["position"] = np.where(data["smas"] > data["smal"], 1, -1)
        data["strategy"] = data.position.shift(1) * data["returns"]
        data.dropna(inplace=True)

        data["trades"] = data.position.diff().fillna(0).abs()

        # correct strategy returns based on trading costs
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

        print("Optimizing strategy...")

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
                current_return = self.test(mute=True)[0]

                if current_return > max_return:
                    max_return = current_return
                    GSMAS = SMAS
                    GSMAL = SMAL

        self.set_params(GSMAS, GSMAL)
        self.test(mute=True)

        print(f"Strategy optimized on interval {self._start} - {self._end}")
        print(f"Max Return: {round(max_return * 100  - 100, 2)}%, Best SMAS: {GSMAS} ({self._granularity}), Best SMAL: {GSMAL} ({self._granularity})")

        return max_return, GSMAS, GSMAL
