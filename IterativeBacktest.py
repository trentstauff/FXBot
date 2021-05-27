from IterativeBase import *

class IterativeBacktest(IterativeBase):

    def go_long(self, bar, units=None, amount=None):
        if self._position == -1:
            # if short, go neutral first
            self.buy(bar, units = -self._units)
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

    # TODO: Make this inheritable by the strategy, make this file more abstract
    def test_sma(self, smas, smal):
        print(f"Testing SMA strategy on {self._symbol} with smas={smas} and smal={smal}")

        # reset instrument attributes
        self._position = 0
        self._trades = 0
        self._current_balance = self._initial_balance
        self.acquire_data()

        self._data["smas"] = self._data.bid_price.rolling(smas).mean()
        self._data["smal"] = self._data.bid_price.rolling(smal).mean()
        self._data.dropna(inplace=True)

        # sma crossover strategy
        for bar in range(len(self._data)-1):
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

        self.close_position(bar+1)
