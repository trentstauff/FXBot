import numpy as np
import matplotlib.pyplot as plt
import tpqoa


class Backtester:
    """Class implementing a vectorized back-testing framework."""
    def __init__(self, instrument, start, end, granularity="D", trading_cost=0):
        """
        Initializes the Backtester object.

        Args:
            instrument (string): A string holding the ticker of instrument to be tested
            start (string): The start date of the testing period
            end (string): The end date of the testing period
            granularity (string) <DEFAULT = "D">: Length of each candlestick for the respective instrument
            trading_cost (float) <DEFAULT = 0.00>: A static trading cost considered when calculating returns
        """
        self._instrument = instrument
        self._start = start
        self._end = end
        self._granularity = granularity
        self._tc = trading_cost

        self._results = None

        self._data = self.acquire_data()
        self._data = self.prepare_data()

    def acquire_data(self):
        """
        A general function to acquire data of instrument from a source.

        Returns:
            Returns a Pandas dataframe containing downloaded info.
        """
        print("Downloading historical data...")

        oanda = tpqoa.tpqoa("oanda.cfg")

        df = oanda.get_history(
            self._instrument, self._start, self._end, self._granularity, "M"
        )

        # only care for the closing price
        df = df.c.to_frame()
        df.rename(columns={"c": "price"}, inplace=True)

        df.dropna(inplace=True)

        df["returns"] = np.log(df.div(df.shift(1)))

        print("Download complete.")

        return df

    def prepare_data(self):
        """
        Prepares data for strategy-specific information.
        Returns:
            Returns a Pandas dataframe
        """
        return self._data.copy()

    def resample(self, granularity):
        """
        Resamples the instruments' dataset to be in buckets of the passed granularity (IE "W", "D", "H").

        Args:
            granularity (string): The new granularity for the dataset
        """
        self._granularity = granularity
        self._data.resample(granularity)
        return

    def get_data(self):
        """
        Getter function to retrieve current instrument's dataframe.

        Returns:
            Returns the stored Pandas dataframe with information regarding the instrument
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

    def test(self):
        """
        Executes the back-testing of the strategy on the set instrument.

        Returns:
            Returns a tuple, (float: performance, float: out_performance)
            -> "performance" is the percentage of return on the interval [start, end]
            -> "out_performance" is the performance when compared to a buy & hold on the same interval
                IE, if out_performance is greater than one, the strategy outperformed B&H.
        """
        pass

    def optimize(self):
        """
        Optimizes the strategy on the interval [start,end] which allows for the greatest return.
        """
        pass

    def plot_results(self):
        """
        Plots the results of test() or optimize().
        Also plots the results of the buy and hold strategy on the interval [start,end] to compare to the results.
        """
        if self._results is not None:
            print("Plotting Results.")
            title = f"{self._instrument}"
            self._results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
            plt.show()
        else:
            print("Please run test() or optimize().")
