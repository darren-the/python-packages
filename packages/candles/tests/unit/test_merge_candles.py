import pytest
from candles.operations import merge_candles
from candles.types import Candle, Timeframe


def test_first_candle():
    first_candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._5m,
        timestamp=1451606400000,
        complete=True,
        open=100,
        close=200,
        high=250,
        low=50
    )
    merged_candle = merge_candles(
        candle=first_candle,
        timeframe=Timeframe._15m
    )
    expected_candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._15m,
        timestamp=1451606400000,
        complete=False,
        open=100,
        close=200,
        high=250,
        low=50
    )
    assert merged_candle == expected_candle


def test_compatible_two_candles():
    candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._5m,
        timestamp=1451606700000,
        complete=True,
        open=200,
        close=150,
        high=300,
        low=40
    )
    prev_candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._15m,
        timestamp=1451606400000,
        complete=False,
        open=100,
        close=200,
        high=250,
        low=50
    )
    merged_candle = merge_candles(
        candle=candle,
        timeframe=Timeframe._15m,
        prev_candle=prev_candle
    )
    expected_candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._15m,
        timestamp=1451606700000,
        complete=False,
        open=100,
        close=150,
        high=300,
        low=40
    )
    assert merged_candle == expected_candle


def test_new_timeframe_candle():
    candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._5m,
        timestamp=1451692800000,
        complete=True,
        open=1200,
        close=1210,
        high=1300,
        low=500
    )
    prev_candle = Candle(
        base_timeframe=Timeframe._1D,
        timeframe=Timeframe._1D,
        timestamp=1451606400000,
        complete=True,
        open=1000,
        close=1200,
        high=1250,
        low=600
    )
    merged_candle = merge_candles(
        candle=candle,
        timeframe=Timeframe._1D,
        prev_candle=prev_candle
    )
    expected_candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._1D,
        timestamp=1451692800000,
        complete=False,
        open=1200,
        close=1210,
        high=1300,
        low=500
    )
    assert merged_candle == expected_candle


def test_new_timeframe_candle_broken():
    candle = Candle(
        base_timeframe=Timeframe._5m,
        timeframe=Timeframe._5m,
        timestamp=1451693100000,
        complete=True,
        open=1200,
        close=1210,
        high=1300,
        low=500
    )
    prev_candle = Candle(
        base_timeframe=Timeframe._1D,
        timeframe=Timeframe._1D,
        timestamp=1451606400000,
        complete=True,
        open=1000,
        close=1200,
        high=1250,
        low=600
    )
    with pytest.raises(ValueError):
        merge_candles(
            candle=candle,
            timeframe=Timeframe._1D,
            prev_candle=prev_candle
        )
    