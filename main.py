import tpqoa
from datetime import datetime

from livetrading.BollingerBandsLive import BollingerBandsLive
from livetrading.ContrarianLive import ContrarianLive
from livetrading.MLClassificationLive import MLClassificationLive
from livetrading.MomentumLive import MomentumLive
from livetrading.SMALive import SMALive

from backtesting.ContrarianBacktest import ContrarianBacktest
from backtesting.BollingerBandsBacktest import BollingerBandsBacktest
from backtesting.MomentumBacktest import MomentumBacktest
from backtesting.SMABacktest import SMABacktest
from backtesting.MLClassificationBacktest import MLClassificationBacktest


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

            print("Please enter the granularity for your session (IE \"1h\", \"1m\", \"5s\"): \n")

            granularity = input("")

            print("Please enter the number of units you'd like to trade with (integer, IE 200000 units): \n")

            units = int(input(""))

            print("Enter stop profit dollars to halt trading at (float, IE 25, 15.34, etc)  (enter \"n\" if not applicable): \n")

            # TODO: Enable stop datetime

            stop_profit = input("")

            if stop_profit == "n":
                stop_profit = None
            else:
                stop_profit = float(stop_profit)

            print("Enter a negative stop loss to halt trading at (float, IE -25, -1.32, etc) (enter \"n\" if not applicable): \n")

            stop_loss = input("")

            if stop_loss == "n":
                stop_loss = None
            else:
                stop_loss = float(stop_loss)

            ###################################################################################
            # Strategies
            ###################################################################################

            if strategy == "sma":

                print("Enter SMAS value (integer, IE 9): \n")

                smas = int(input(""))

                print("Enter SMAL value (integer, IE 20): \n")

                smal = int(input(""))

                while smal < smas:
                    smal = int(input("SMAL must be larger or equal to SMAS: \n"))

                trader = SMALive(cfg, instrument, granularity, smas, smal, units, stop_loss=stop_loss, stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "bollinger_bands":

                print("Enter SMA value (integer, IE 9): \n")

                sma = int(input(""))

                print("Enter deviation value (integer, IE 2): \n")

                deviation = int(input(""))

                trader = BollingerBandsLive(cfg, instrument, granularity, sma, deviation, units, stop_loss=stop_loss,
                                 stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "momentum":

                print("Enter window value (integer, IE 3): \n")

                window = int(input(""))

                trader = MomentumLive(cfg, instrument, granularity, window, units, stop_loss=stop_loss,
                                 stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "contrarian":

                print("Enter window value (integer, IE 3): \n")

                window = int(input(""))

                trader = ContrarianLive(cfg, instrument, granularity, window, units, stop_loss=stop_loss,
                                      stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "ml_classification":

                print("Enter number of lags (integer, IE 6): \n")

                lags = int(input(""))

                trader = MLClassificationLive(cfg, instrument, granularity, lags, units, stop_loss=stop_loss,
                                 stop_profit=stop_profit)

                # TODO: Post trading analysis, maybe some graphs etc

        else:

            backtesting_strategies = ["sma", "bollinger_bands", "contrarian", "momentum", "ml_classification", "ml_regression"]

            print("Please choose the strategy you would like to backtest: \n")

            for strategy in backtesting_strategies:
                print(strategy, end=", ")

            choice = input("\n").lower()

            while choice not in backtesting_strategies:
                choice = input("Please choose a strategy listed above. \n").lower()

            strategy = choice

            print("Enter the start date for the backtest (string, in form of \"YYYY-MM-DD\"): \n")

            start = input("")

            print("Enter the end date for the backtest (string, in form of \"YYYY-MM-DD\"): \n")

            end = input("")

            while datetime.strptime(start, '%Y-%m-%d') > datetime.strptime(end, '%Y-%m-%d'):
                end = input("End date must be after start date. \n")

            print("Enter the trading cost to consider: (float, IE 0.0, 0.00007): \n")

            trading_cost = float(input(""))

            print("Please enter the granularity for your session (IE \"1h\", \"1m\", \"5s\"): \n")

            granularity = input("")

            if strategy == "sma":

                print("Enter SMAS value (integer, IE 9): \n")

                smas = int(input(""))

                print("Enter SMAL value (integer, IE 20): \n")

                smal = int(input(""))

                while smal < smas:
                    smal = int(input("SMAL must be larger or equal to SMAS: \n"))

                trader = SMABacktest(instrument, start, end, smas, smal, granularity, trading_cost)

                trader.test()
                trader.optimize()
                trader.plot_results()

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "bollinger_bands":

                print("Enter SMA value (integer, IE 9): \n")

                sma = int(input(""))

                print("Enter deviation value (integer, IE 2): \n")

                deviation = int(input(""))

                trader = BollingerBandsBacktest(instrument, start, end, sma, deviation, granularity, trading_cost)

                trader.test()
                trader.optimize()
                trader.plot_results()

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "momentum":

                print("Enter window value (integer, IE 3): \n")

                window = int(input(""))

                trader = MomentumBacktest(instrument, start, end, window, granularity, trading_cost)

                trader.test()
                trader.optimize()
                trader.plot_results()

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "contrarian":

                print("Enter window value (integer, IE 3): \n")

                window = int(input(""))

                trader = ContrarianBacktest(instrument, start, end, window, granularity, trading_cost)

                trader.test()
                trader.optimize()
                trader.plot_results()

                # TODO: Post trading analysis, maybe some graphs etc

            elif strategy == "ml_classification":

                trader = MLClassificationBacktest(instrument, start, end, granularity, trading_cost)

                trader.test()
                trader.plot_results()

                # TODO: Post trading analysis, maybe some graphs etc
