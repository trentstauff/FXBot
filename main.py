import tpqoa
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

from livetrading.BollingerBandsLive import BollingerBandsLive
from livetrading.ContrarianLive import ContrarianLive
from livetrading.MLClassificationLive import MLClassificationLive
from livetrading.MomentumLive import MomentumLive
from livetrading.SMALive import SMALive

from backtesting.IterativeBacktest import IterativeBacktest
from backtesting.ContrarianBacktest import ContrarianBacktest
from backtesting.BollingerBandsBacktest import BollingerBandsBacktest
from backtesting.MomentumBacktest import MomentumBacktest
from backtesting.MultipleRegressionModelPredictor import MultipleRegressionModelPredictor
from backtesting.SMABacktest import SMABacktest
from backtesting.MLClassificationBacktest import MLClassificationBacktest

def check_input(input):
    if input == "q":
        return False
    return True


if __name__ == "__main__":

    while True:

        # step 1 ensure they have this
        cfg = "oanda.cfg"

        # step 1.5 open oanda connection
        oanda = tpqoa.tpqoa("oanda.cfg")

        # step 2 decide instrument

        print("Enter an instrument to trade: \n")
        choices = []
        for instrument in oanda.get_instruments():
            temp = instrument[1]
            choices.append(temp)
            print(temp, end=", ")

        print("")

        choice = input("\n")

        while choice not in choices:
            choice = input("Please choose an instrument from the list above: ")

        instrument = choice

        # step 3 decide if live or backtesting

        choice = input("Live Trading (1) or Backtesting (2)? \n")

        while choice not in ["1", "2"]:
            choice = input("Please choose between \"1\" or \"2\": \n")

        # step 4, depending on decision, showcase available strategies

        if choice == "1":
            live_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification"]

            print("Please choose the strategy you would like to utilize: \n")

            for strategy in live_strategies:
                print(strategy, end=", ")

            choice = input("\n").lower()

            while choice not in live_strategies:
                choice = input("Please choose a strategy listed above. \n").lower()

            strategy = choice

            # TODO: Validation
            print("Please enter the granularity for your session (IE \"1h\", \"1m\", \"5s\"): \n")

            granularity = input("")

            print("Please enter the number of units you'd like to trade with: \n")

            # TODO: Validation
            units = int(input(""))

            print("Enter stop profit to halt trading at, IE 25$ (enter \"n\" if not applicable): \n")

            # TODO: Enable stop datetime

            # TODO: Validation that it is an int
            stop_profit = input("")

            if stop_profit == "n":
                stop_profit = None
            else:
                stop_profit = float(stop_profit)

            print("Enter stop loss to halt trading at, IE -25$ (enter \"n\" if not applicable): \n")

            # TODO: Validation that it is an int
            stop_loss = input("")

            if stop_loss == "n":
                stop_loss = None
            else:
                stop_loss = float(stop_loss)

            ###################################################################################
            # Strategies
            ###################################################################################

            if strategy == "sma":

                print("Enter SMAS value: \n")

                # TODO: Validation that it is an int
                smas = int(input(""))

                print("Enter SMAL value: \n")

                # TODO: Validation that it is an int
                smal = int(input(""))

                while smal < smas:
                    smal = int(input("SMAL must be larger or equal to SMAS: \n"))

                trader = SMALive(cfg, instrument, granularity, smas, smal, units, stop_loss=stop_loss, stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "bollinger_bands":

                print("Enter SMA value: \n")

                # TODO: Validation that it is an int
                sma = int(input(""))

                print("Enter deviation value: \n")

                # TODO: Validation that it is an int
                deviation = int(input(""))

                trader = BollingerBandsLive(cfg, instrument, granularity, sma, deviation, units, stop_loss=stop_loss,
                                 stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "momentum":

                print("Enter window value: \n")

                # TODO: Validation that it is an int
                window = int(input(""))

                trader = MomentumLive(cfg, instrument, granularity, window, units, stop_loss=stop_loss,
                                 stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "contrarian":

                print("Enter window value: \n")

                # TODO: Validation that it is an int
                window = int(input(""))

                trader = ContrarianLive(cfg, instrument, granularity, window, units, stop_loss=stop_loss,
                                      stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "ml_classification":

                print("Enter number of lags: \n")

                # TODO: Validation that it is an int
                lags = int(input(""))

                trader = MLClassificationLive(cfg, instrument, granularity, lags, units, stop_loss=stop_loss,
                                 stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            break

        else:

            backtesting_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification", "ml_regression"]
            required_backtesting_params = {
                "all": [["start", None], ["end", None], ["trading_cost", 0], ["granularity", None]],
                "sma": [["smas", None], ["smal", None]],
                "momentum": [["window", None]],
                "contrarian": [["window", None]],
                "bollinger_bands": [["sma", None], ["deviation", None]],
                "ml_classification": [["lags", None]],
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
