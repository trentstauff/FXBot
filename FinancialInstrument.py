import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use("seaborn")


# TODO: add docstrings
class FinancialInstrument:

    def __init__(self, ticker, start, end):
        self._ticker = ticker
        self._start = start
        self._end = end

        self.data = self.download_data()
        self.log_returns()

    def __repr__(self):
        return f"FinancialInstrument( ticker=\"{self._ticker}\", start=\"{self._start}\", end=\"{self._end}\" )"

    # Downloads the closing price for the interval of [start, end]
    def download_data(self):
        # Implement try catch (yf does handle it but exits the program)
        download = yf.download(self._ticker, self._start, self._end).Close.to_frame()
        download.rename(columns={"Close": "price"}, inplace=True)
        return download

    # Calculates the running log return of an instrument starting from the start date
    def log_returns(self):
        self.data["log_returns"] = np.log(self.data.price / self.data.price.shift(1)).mul(100)

    def plot_prices(self):
        self.data.price.plot(figsize = (12, 8))
        plt.title(f"Price Chart: {self._ticker}", fontsize=15)
        plt.show()

    def plot_returns(self, style = "ts"):
        if style == "ts":
            self.data.log_returns.plot(figsize=(12, 8))
            plt.title(f"Returns: {self._ticker}", fontsize=15)
        elif style == "hist":
            self.data.log_returns.hist(figsize=(12, 8), bins=int(np.sqrt(len(self.data))))
            plt.title(f"Frequency of Returns: {self._ticker}", fontsize=15)
        plt.show()

    def get_ticker(self):
        return self._ticker

    def set_ticker(self, ticker):
        self._ticker = ticker
        self.data = self.download_data()
        self.log_returns()

    def mean_return(self, freq = None):
        if freq is not None:
            price = self.data.price.resample(freq).last()
            returns = np.log(price / price.shift(1))
            return returns.mean()
        else:
            return self.data.log_returns.mean()

    def std_return(self, freq = None):
        if freq is not None:
            price = self.data.price.resample(freq).last()
            returns = np.log(price / price.shift(1))
            return returns.std()
        else:
            return self.data.log_returns.std()

    def annualized_RR(self):
        # To annualize performance, we extrapolate the data for 252 trading days
        mean_return = round(self.data.log_returns.mean() * 252, 3)
        risk = round(self.data.log_returns.std() * np.sqrt(252), 3)
        info = [mean_return, risk]
        return info

    # # https://www.fool.com/investing/2018/03/21/9-essential-metrics-all-smart-investors-should-kno.aspx
    # def PE_ratio(self):
    #     pass
    #
    # def P2S_ratio(self):
    #     pass
    #
    # def PEG_ratio(self):
    #     pass

