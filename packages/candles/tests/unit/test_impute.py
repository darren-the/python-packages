import pytest
from candles.clients.exchange.exchangebase import Client
from candles.types import Timeframe, Candle
from candles.exceptions import NothingToImputeError


def test_impute_candles():
    client = Client(interval=Timeframe._1m.ms)
    first_candle = Candle(
        base_timeframe=Timeframe._1m,
        timeframe=Timeframe._1m,
        timestamp=1750377600000,
        complete=True,
        open=100,
        close=200,
        high=200,
        low=100
    )
    second_candle = Candle(
        base_timeframe=Timeframe._1m,
        timeframe=Timeframe._1m,
        timestamp=1750377780000,
        complete=True,
        open=200,
        close=300,
        high=300,
        low=200
    )
    imputed_candles = list(client.impute_candles(second_candle, first_candle))
    assert len(imputed_candles) == 2
    assert imputed_candles == [first_candle.copy(timestamp=1750377660000), first_candle.copy(timestamp=1750377720000)]


def test_nothing_to_impute():
    client = Client(interval=Timeframe._1m.ms)
    first_candle = Candle(
        base_timeframe=Timeframe._1m,
        timeframe=Timeframe._1m,
        timestamp=1750377600000,
        complete=True,
        open=100,
        close=200,
        high=200,
        low=100
    )
    second_candle = Candle(
        base_timeframe=Timeframe._1m,
        timeframe=Timeframe._1m,
        timestamp=1750377660000,
        complete=True,
        open=200,
        close=300,
        high=300,
        low=200
    )
    with pytest.raises(NothingToImputeError):
        list(client.impute_candles(second_candle, first_candle))
