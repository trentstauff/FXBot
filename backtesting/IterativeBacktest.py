from backtesting.IterativeBase import IterativeBase


class IterativeBacktest(IterativeBase):

    """Class implementing strategy specific iterative testing functions"""
    def go_long(self, bar, units=None, amount=None):
        if self._position == -1:
            # if short, go neutral first
            self.buy(bar, units=-self._units)
        if units:
            self.buy(bar, units=units)
        elif amount:
            if amount == "all":
                amount = self._current_balance
            self.buy(bar, amount=amount)

    def go_short(self, bar, units=None, amount=None):
        if self._position == 1:
            self.sell(bar, units=self._units)
        if units:
            self.sell(bar, units=units)
        elif amount:
            if amount == "all":
                amount = self._current_balance
            self.sell(bar, amount=amount)

    def reset(self):
        # reset instrument attributes
        self._position = 0
        self._trades = 0
        self._current_balance = self._initial_balance
        self.acquire_data()

    # TODO: Make this inheritable by the strategy, make this file more abstract
    def test_sma(self, smas, smal):
        print(
            f"Testing SMA strategy on {self._symbol} with smas={smas} and smal={smal}"
        )

        self.reset()

        self._data["smas"] = self._data.bid_price.rolling(smas).mean()
        self._data["smal"] = self._data.bid_price.rolling(smal).mean()
        self._data.dropna(inplace=True)

        # sma crossover strategy
        for bar in range(len(self._data) - 1):
            if self._data["smas"].iloc[bar] > self._data["smal"].iloc[bar]:
                # go long
                if self._position in [0, -1]:
                    # go long with entire balance to switch position
                    self.go_long(bar, amount="all")
                    self._position = 1
            elif self._data["smas"].iloc[bar] < self._data["smal"].iloc[bar]:
                # go short
                if self._position in [0, 1]:
                    # go short with entire balance to switch position
                    self.go_short(bar, amount="all")
                    self._position = -1

        self.close_position(bar + 1)

    def test_contrarian(self, window=1):
        print(f"Testing Contrarian strategy on {self._symbol} with window={window}")

        self.reset()

        # prepares the data
        self._data["rolling_returns"] = self._data["returns"].rolling(window).mean()
        self._data.dropna(inplace=True)

        for bar in range(len(self._data) - 1):
            if self._data["rolling_returns"].iloc[bar] <= 0:
                # go long
                if self._position in [0, -1]:
                    self.go_long(bar, amount="all")
                    self._position = 1
            else:
                # go short
                if self._position in [0, 1]:
                    self.go_short(bar, amount="all")
                    self._position = -1

        self.close_position(bar + 1)

    def test_momentum(self, window=1):
        print(f"Testing Momentum strategy on {self._symbol} with window={window}")

        self.reset()

        # prepares the data
        self._data["rolling_returns"] = self._data["returns"].rolling(window).mean()
        self._data.dropna(inplace=True)

        for bar in range(len(self._data) - 1):
            if self._data["rolling_returns"].iloc[bar] <= 0:
                # go short
                if self._position in [0, 1]:
                    self.go_short(bar, amount="all")
                    self._position = -1
            else:
                # go long
                if self._position in [0, -1]:
                    self.go_long(bar, amount="all")
                    self._position = 1

        self.close_position(bar + 1)

    def test_bollinger_bands(self, sma, std=2):
        print(
            f"Testing Bollinger Bands strategy on {self._symbol} with sma={sma}, std={std}"
        )

        self.reset()

        # prepares the data
        self._data["sma"] = self._data.bid_price.rolling(sma).mean()
        self._data["lower"] = self._data["sma"] - (
            self._data.bid_price.rolling(sma).std() * std
        )
        self._data["upper"] = self._data["sma"] + (
            self._data.bid_price.rolling(sma).std() * std
        )

        self._data.dropna(inplace=True)

        for bar in range(len(self._data) - 1):

            if self._position == 0:

                if self._data["bid_price"].iloc[bar] < self._data["lower"].iloc[bar]:
                    # if price is lower than lower band, indicates oversold, and to go long
                    self.go_long(bar, amount="all")
                    self._position = 1
                elif self._data["bid_price"].iloc[bar] > self._data["upper"].iloc[bar]:
                    # if price is higher than upper band, indicates overbought, and to go short
                    self.go_short(bar, amount="all")
                    self._position = -1

            elif self._position == 1:
                if self._data["bid_price"].iloc[bar] > self._data["sma"].iloc[bar]:

                    # if price crosses upper band, signal to go short
                    if (
                        self._data["bid_price"].iloc[bar]
                        > self._data["upper"].iloc[bar]
                    ):
                        self.go_short(bar, amount="all")
                        self._position = -1
                    else:
                        # if price is between sma and upper, just go neutral
                        self.sell(bar, units=self._units)
                        self._position = 0

            elif self._position == -1:
                if self._data["bid_price"].iloc[bar] < self._data["sma"].iloc[bar]:

                    # if price crosses lower band, signal to go long
                    if (
                        self._data["bid_price"].iloc[bar]
                        < self._data["lower"].iloc[bar]
                    ):
                        self.go_long(bar, amount="all")
                        self._position = 1
                    else:
                        # if price is between lower and sma, just go neutral
                        self.buy(bar, units=-self._units)
                        self._position = 0

        self.close_position(bar + 1)
