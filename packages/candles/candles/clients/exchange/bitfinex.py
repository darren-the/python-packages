import requests
from enum import Enum
from candles.clients.exchange import exchangebase
from candles.types import Timeframe, Candle


class Symbol(str, Enum):
    BTCUSD = "BTCUSD"
    ETHUSD = "ETHUSD"

    def __str__(self):
        return self.value


class UpdateMethod(str, Enum):
    hist = "hist"
    live = "live"

    def __str__(self):
        return self.value


class Client(exchangebase.Client):
    req_limit_per_min = 10_000

    def __init__(
        self,
        timeframe: Timeframe,
        symbol: Symbol,
        update_method: UpdateMethod = UpdateMethod.hist
    ):
        self.timeframe = timeframe
        self.symbol = symbol
        self.update_method = update_method
        super().__init__(interval=timeframe.ms)

    @property
    def url(self):
        base_url = "https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:t{symbol}/{update_method}"
        return base_url.format(
            timeframe=self.timeframe,
            symbol=self.symbol,
            update_method=self.update_method
        )

    def fetch_raw_candles(self, start: int, end: int):
        payload = {
            'start': start,
            'end': end,
            'sort': 1,
            'limit': self.req_limit_per_min,
        }
        data = requests.get(self.url, params=payload).json()
        for row in data:
            yield Candle(
                base_timeframe=self.timeframe,
                timeframe=self.timeframe,
                timestamp=row[0],
                open=row[1],
                close=row[2],
                high=row[3],
                low=row[4],
            )
