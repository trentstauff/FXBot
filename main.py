import pandas as pd
import tpqoa
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("seaborn")
from FinancialInstrument import FinancialInstrument
from SMATest import SMATest
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


# def api_info():
#     # Use a breakpoint in the code line below to debug your script
#     oanda = tpqoa.tpqoa('oanda.cfg')
#
#     print(oanda.account_type)
#     print(oanda.account_id)
#     print(oanda.get_instruments())
#     df = oanda.get_history("EUR_USD", "2020-07-01", "2020-07-31", "D", "B")
#     print(df)
#     print(df.info())
#     # oanda.stream_data('USD_CAD', stop=10)
#     oanda.create_order("EUR_USD", 100000, sl_distance=0.1)
#
#     x = 0
#     while(x < 1000000000):
#         x += 1
#
#     oanda.create_order("EUR_USD", -100000, sl_distance=0.1)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    obj = SMATest("EURUSD", 30, 200, "2004-01-01", "2020-06-30")
    print(obj.test_sma())
    obj.plot_results()
    print(obj.optimize_sma())
    obj.plot_results()
