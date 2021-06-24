import tpqoa
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

from livetrading.BollingerBandsLive import BollingerBandsLive

from backtesting.IterativeBacktest import IterativeBacktest

from backtesting.ContrarianBacktest import ContrarianBacktest
from backtesting.BollingerBandsBacktest import BollingerBandsBacktest
from backtesting.MomentumBacktest import MomentumBacktest
from backtesting.MultipleRegressionModelPredictor import MultipleRegressionModelPredictor
from backtesting.SMABacktest import SMABacktest
from backtesting.MLClassificationBacktest import MLClassificationBacktest

if __name__ == "__main__":

    # step 1 ensure they have this
    cfg = "oanda.cfg"

    # step 1.5 open oanda connection
    oanda = tpqoa.tpqoa("oanda.cfg")

    # step 2 decide instrument
    instrument = None
    print(oanda.get_instruments())

    # step 3 decide if live or backtesting

    print("Live Trading (1) or Backtesting (2)?")

    choice = None

    # step 4, depending on decision, showcase available strategies
    live_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification"]
    backtesting_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification", "ml_regression"]

    live_params = ["bar_length", "units", "history_days", "stop_datetime", "stop_profit"]

    required_live_params = {
        "all": [["bar_length", None], ["units", None], ["history_days", None], ["stop_datetime", None], ["stop_profit", None]],
        "sma": [["smas", None], ["smal", None]],
        "momentum": [["window", None]],
        "contrarian": [["window", None]],
        "bollinger_bands": [["sma", None], ["deviation", None]]
        "ml_classification": [],
        "ml_regression": [["backtest_range", None], ["forwardtest_range", None], ["lags", None]]
    }

    required_backtesting_params = {
        "all": [["start", None], ["end", None], ["trading_cost", 0], ["granularity", None]],
        "sma": [["smas", None], ["smal", None]],
        "momentum": [["window", None]],
        "contrarian": [["window", None]],
        "bollinger_bands": [["sma", None], ["deviation", None]]
        "ml_classification": [],
        "ml_regression": [["backtest_range", None], ["forwardtest_range", None], ["lags", None]]
    }


    # obj = SMABacktest("EUR_USD", "2010-01-01", "2020-06-30", 30, 200, "D", 0)
    # obj.test()
    # obj.plot_results()
    # print(obj.get_results())
    # obj.optimize()
    # obj = SMABacktest("EUR_USD", 30, 200, "2010-01-01", "2020-06-30", "D", 0.1)
    # print(obj.test())
    # obj.plot_results()
    # print(obj.get_results())
    # print(obj.optimize())
    # obj.plot_results()
    # obj.plot_results()

    # obj = ContrarianBacktest("EUR_USD", "2010-01-01", "2020-06-30", 20, "D", 0)
    # obj.test()
    # obj.plot_results()
    # obj.optimize()
    # obj.plot_results()
    # print(obj)

    # obj = MomentumBacktest("EUR_USD", "2010-01-01", "2020-06-30", window=1, granularity="D", trading_cost=0)
    #
    # obj.test()
    # obj.plot_results()
    # obj.optimize()
    # obj.plot_results()
    # print(obj)

    # obj = MomentumBacktest("EUR_USD", "2010-01-01", "2020-06-30", 20, "D", 0.0001)
    # print(obj.optimize())
    # obj.plot_results()

    # obj = MultipleRegressionModelPredictor("EUR_USD", ("2019-01-01", "2019-12-30"), ("2020-01-01", "2020-08-30"), 5, granularity="M30", trading_cost=0.000015)
    # obj.test()
    # obj.plot_results()
    # obj.get_hitratio()

    # obj = MLClassificationBacktest("EUR_USD", "2019-01-01", "2020-08-30", granularity="M5", trading_cost=0)
    # print(obj.get_data())
    # obj.test()
    #
    # obj.plot_results()
    # obj.get_hitratio()

    # obj = IterativeBacktest(
    #     "oanda.cfg",
    #     "EUR_USD",
    #     "2006-12-31",
    #     "2020-06-30",
    #     100000,
    #     granularity="D",
    #     use_spread=False,
    # )
    # obj.test_contrarian(1)
    # stop = datetime(2021, 6, 21, 21, 4, 6)



    # api_info()

    # helpers.find_optimal_trading_time("oanda.cfg", "EUR_USD", "2019-07-21", "2020-10-20", granularity="1H")
    # td = BollingerBandsLive("oanda.cfg", "EUR_USD", "1m", sma=20, deviation=1, units=100000, stop_loss=-5)
    # print("starting stream")
    # print(td._data)

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
