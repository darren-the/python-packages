import pytest
from candles.clients.exchange.exchangebase import Client
from candles.types import Timeframe, Candle


CANDLE_1 = Candle(
    base_timeframe=Timeframe._1m,
    timeframe=Timeframe._1m,
    timestamp=1750377600000,
    complete=True,
    open=100,
    close=200,
    high=200,
    low=100
)

CANDLE_2 = Candle(
    base_timeframe=Timeframe._1m,
    timeframe=Timeframe._1m,
    timestamp=1750377780000,
    complete=True,
    open=200,
    close=300,
    high=300,
    low=200
)

@pytest.fixture
def raw_candles(mocker):
    return mocker.patch(
        "candles.clients.exchange.exchangebase.Client.fetch_raw_candles",
        return_value=[
            CANDLE_1,
            CANDLE_2
        ]
    )

def test_fetch_candles(raw_candles):
    client = Client(interval=Timeframe._1m.ms)
    client.req_limit_per_min = 9999
    candles = list(client.fetch_candles(start=1750377600000, end=1750377780000))  # hacky way to simulate one batch
    assert len(candles) == 4
    assert candles == [CANDLE_1, CANDLE_1.copy(timestamp=1750377660000), CANDLE_1.copy(timestamp=1750377720000), CANDLE_2]
