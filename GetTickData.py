import pandas as pd
from datetime import datetime
import tpqoa


class GetTickData(tpqoa.tpqoa):

    def __init__(self, cfg, instrument, bar_length):
        # passes the config file to tpqoa
        super().__init__(cfg)
        self._instrument = instrument
        self._bar_length = pd.to_timedelta(bar_length)
        self._tick_data = pd.DataFrame()
        self._data = pd.DataFrame()
        self._last_tick = pd.to_datetime(datetime.utcnow()).tz_localize("UTC")

    # called when new streamed data is successful
    def on_success(self, time, bid, ask):
        print(time, bid, ask)

        recent_tick = pd.to_datetime(time)

        df = pd.DataFrame({"bid": bid, "ask": ask, "mid": (ask+bid)/2}, index=[recent_tick])
        self._tick_data = self._tick_data.append(df)

        # resamples the tick data (if applicable), while also dropping
        # the last row (as it can be far off the resampled granularity)
        if (recent_tick - self._last_tick) > self._bar_length:

            # append the most recent resampled ticks to self._data
            self._data = self._data.append(self._tick_data.resample(self._bar_length, label="right").last().ffill().iloc[:-1])

            # only keep the last tick bar (which is a pandas DataFrame)
            self._tick_data = self._tick_data.iloc[-1:]
            self._last_tick = self._data.index[-1]

