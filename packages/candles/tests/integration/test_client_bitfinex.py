from candles.clients.exchange import bitfinex
from candles.types import Timeframe, Candle

def test_fetch_raw_candles():
    client = bitfinex.Client(
        timeframe=Timeframe._1D,
        symbol=bitfinex.Symbol.BTCUSD
    )
    raw_candles = list(client.fetch_raw_candles(
        start=1451606400000,
        end=1451779200000
    ))
    expected_candles = [
        Candle(
            base_timeframe=Timeframe._1D,
            timeframe=Timeframe._1D,
            timestamp=1451606400000,
            open=429.17,
            close=433.98,
            high=436.49,
            low=426.26,
            complete=True
        ), 
        Candle(
            base_timeframe=Timeframe._1D,
            timeframe=Timeframe._1D,
            timestamp=1451692800000,
            open=433.89,
            close=432.7,
            high=435.8,
            low=430,
            complete=True
        ),
        Candle(
            base_timeframe=Timeframe._1D,
            timeframe=Timeframe._1D,
            timestamp=1451779200000,
            open=432.66,
            close=428.39,
            high=433.07,
            low=421.73,
            complete=True
        )
    ]
    assert raw_candles == expected_candles
