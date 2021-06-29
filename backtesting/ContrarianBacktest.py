import numpy as np

from backtesting.Backtester import Backtester


class ContrarianBacktest(Backtester):
    """Class implementing vectorized back-testing of a Contrarian Strategy."""
    def __init__(self, instrument, start, end, window=1, granularity="D", trading_cost=0):
        """
        Initializes the ContrarianBacktest object.

        Args:
            instrument (string): A string holding the ticker symbol of instrument to be tested
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            window (int) <DEFAULT = 1>: Length of lags that drives the position.
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._window = window

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
        return f"ContrarianBacktest( symbol={self._instrument}, start={self._start}, end={self._end}, granularity={self._granularity}, lags={self._window}, trading_cost={self._tc} )"

    def test(self, window=1, mute=False):
        """
        Executes the back-testing of the Contrarian strategy on the set instrument.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """
        if not mute:
            print(f"Testing strategy with window = {window} ...")

        # IE if no lags parameter included and we have a stored lags, use that as the lags instead
        if self._window != 1 and window == 1:
            window = self._window

        data = self._data.copy()

        data["position"] = -np.sign(data["returns"].rolling(window).mean())
        data["strategy"] = data["position"].shift(1) * data["returns"]

        data.dropna(inplace=True)

        # running total of amount of trades, each change of position is 2 trades
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
            print(f"Return: {round(performance*100 - 100,2) }%, Out Performance: {round(out_performance*100,2)}%")

        return performance, out_performance

    def optimize(self, window_range=(1, 252)):
        """
        Optimizes the lags on the interval [start,end] which allows for the greatest return.

        Args:
            window_range (tuple(int, int)) <DEFAULT>=(1,252): Range of values for optimization of sliding lags

        Returns:
            Returns a tuple, (float: max_return, int: best_window)
            -> "max_return" is the optimized (maximum) return rate of the instrument on the interval [start,end]
            -> "best_window" is the optimized lags that enables a maximum return
        """
        if window_range[0] >= window_range[1]:
            print("The range must satisfy: (X,Y) -> X < Y")
            return

        print("Optimizing strategy...")

        max_return = float("-inf")
        best_window = 1

        for window in range(window_range[0], window_range[1]):

            if window == (window_range[1] / 4):
                print("25%...")
            if window == (window_range[1] / 2):
                print("50%...")
            if window == (window_range[1] / 1.5):
                print("75%...")

            current_return = self.test(window, mute=True)[0]

            if current_return > max_return:
                max_return = current_return
                best_window = window

        # save the optimized lags
        self._window = best_window

        # run the final test to store results
        self.test(self._window, mute=True)

        print(f"Strategy optimized on interval {self._start} - {self._end}")
        print(f"Max Return: {round(max_return * 100 - 100,2) - 100}%, Best Window: {best_window} ({self._granularity})")

        return max_return, best_window
