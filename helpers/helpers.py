
import tpqoa

import matplotlib.pyplot as plt
plt.style.use("seaborn")


class helpers():

    def find_optimal_trading_time(cfg, instrument, start, end, granularity="M5"):

        # WARNING: the smaller the granularity, the less frequently the price change will
        # be able to cover the trading costs

        oanda = tpqoa.tpqoa(cfg)

        bid_price = oanda.get_history(instrument=instrument, start=start, end=end, granularity="M5", price="B", localize=False).c.dropna().to_frame()
        ask_price = oanda.get_history(instrument=instrument, start=start, end=end, granularity="M5", price="A", localize=False).c.dropna().to_frame()

        if granularity != "M5":
            bid_price = bid_price.resample(granularity).last().dropna()
            ask_price = ask_price.resample(granularity).last().dropna()

        spread = ask_price - bid_price
        data = bid_price

        data.rename(columns={"c": "bid_price"}, inplace=True)

        data["ask_price"] = ask_price
        data["mid_price"] = ask_price - spread
        data["spread"] = spread

        data["hour"] = data.index.hour

        data["price_change"] = data["mid_price"].diff().abs()

        data["covered_costs"] = data["price_change"] > data["spread"]

        hourly_grouping = data.groupby("hour")["covered_costs"].mean()

        hourly_grouping.plot(kind="bar", figsize=(12,8), fontsize=13)
        plt.xlabel("UTC Hour")
        plt.ylabel("Percentage of Costs Covered")
        plt.title(f"Granularity = {granularity}")

        plt.show()

        return hourly_grouping

