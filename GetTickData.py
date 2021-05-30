import pandas as pd
import tpqoa


class GetTickData(tpqoa.tpqoa):

    def __init__(self, cfg):
        # passes the config file to tpqoa
        super().__init__(cfg)
        self._tick_data = pd.DataFrame()

    def on_success(self, time, bid, ask):
        print(time,bid,ask)
        df = pd.DataFrame({"bid": bid, "ask": ask, "mid": (ask+bid)/2}, index=[pd.to_datetime(time)])
        self._tick_data = self._tick_data.append(df)

