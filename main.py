import pandas as pd
import tpqoa
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

from MultipleRegressionModelPredictor import MultipleRegressionModelPredictor
from BollingerBandsBacktest import BollingerBandsBacktest
from MLClassificationBacktest import MLClassificationBacktest
from IterativeBase import IterativeBase
from IterativeBacktest import IterativeBacktest
from GetTickData import GetTickData

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
    df = oanda.get_history("EUR_USD", "2020-01-01", "2020-12-31", "M30", "B")
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

    # obj = MultipleRegressionModelPredictor("EUR_USD", ("2019-01-01", "2019-12-30"), ("2020-01-01", "2020-08-30"), 5, granularity="M30", trading_cost=0.000015)
    # print(obj.get_data())
    # obj.test()
    #
    # obj.plot_results()
    # print(obj.get_hitratio())

    # obj = MLClassificationBacktest("EUR_USD", "2019-01-01", "2020-08-30", granularity="M5", trading_cost=0)
    # print(obj.get_data())
    # obj.test()
    #
    # obj.plot_results()
    # print(obj.get_hitratio())

    # obj = IterativeBacktest("EUR_USD", "2006-12-31", "2020-06-30", 100000, granularity="D", use_spread=True)
    # obj.test_sma(50,200)

    td = GetTickData("oanda.cfg")
    td.stream_data("EUR_USD", stop = 10)
    # obj.test_contrarian(window=3)
    # obj.test_bollinger_bands(50)
    # obj.print_current_balance(0)
    # obj.print_current_position_value(0)
    # obj.print_current_balance(-1)
    # obj.print_current_position_value(-1)
    # obj.print_current_nav(-1)
    # obj.close_position(-1)
    # print(obj._data)
    # obj.close_position(-1)
    # obj.plot_data("spread")
    # print(obj.bar_info(100))


