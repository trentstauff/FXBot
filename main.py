import pandas as pd
import tpqoa
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

from MultipleRegressionModelPredictor import MultipleRegressionModelPredictor
from BollingerBandsBacktest import BollingerBandsBacktest

plt.style.use("seaborn")
from FinancialInstrument import FinancialInstrument
from SMABacktest import SMABacktest
from ContrarianBacktest import ContrarianBacktest
from MomentumBacktest import MomentumBacktest
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def yahoo():
    tickers = ["AAPL", "BB", "TD"]
    stocks = yf.download(tickers, start = "2010-01-01", end = "2019-02-06")
    close = stocks.loc[:, "Close"].copy()
    norm = close.div(close.iloc[0]).mul(100)
    norm.plot(figsize= (15,8), fontsize = 13)
    plt.legend(fontsize = 13)
    plt.show()


def api_info():
    # Use a breakpoint in the code line below to debug your script
    oanda = tpqoa.tpqoa('oanda.cfg')

    # print(oanda.account_type)
    # print(oanda.account_id)
    print(oanda.get_instruments())
    # TODO USE THIS TO GET HISTORICAL DATA!!!!!!!!!!!!!!
    df = oanda.get_history("EUR_USD", "2020-01-01", "2020-12-31", "D", "B")
    print(df)
    # print(df.info())
    # # oanda.stream_data('USD_CAD', stop=10)
    # oanda.create_order("EUR_USD", 100000, sl_distance=0.1)
    #
    # x = 0
    # while(x < 1000000000):
    #     x += 1
    #
    # oanda.create_order("EUR_USD", -100000, sl_distance=0.1)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # api_info()

    # obj = SMABacktest("EUR_USD", 30, 200, "2010-01-01", "2020-06-30", "D", 0)
    # print(obj.test())
    # obj.plot_results()
    # print(obj.get_results())
    # print(obj.optimize())
    # obj = SMABacktest("EUR_USD", 30, 200, "2010-01-01", "2020-06-30", "D", 0.1)
    # print(obj.test())
    # obj.plot_results()
    # print(obj.get_results())
    # print(obj.optimize())
    # obj.plot_results()
    # obj.plot_results()

    # obj = ContrarianBacktest("EUR_USD", "2010-01-01", "2020-06-30", 20, "D", 0)
    # print(obj.optimize())
    # obj.plot_results()
    #
    # obj = MomentumBacktest("EUR_USD", "2010-01-01", "2020-06-30", 20, "D", 0.0001)
    # print(obj.optimize())
    # obj.plot_results()

    obj = MultipleRegressionModelPredictor("EUR_USD", ("2019-01-01", "2019-12-30"), ("2020-01-01", "2020-08-30"), 5, granularity="M5", trading_cost=0)
    print(obj.get_data())
    obj.test()

    obj.plot_results()
    print(obj.get_hitratio())


