from candles.types import Candle, Timeframe, RSI
from candles.utils import round_down_to_nearest_interval, time_passed_interval_start, morph_prev_timeseries_obj


def merge_candles(
    candle: Candle,
    timeframe: Timeframe,
    prev_candle: Candle | None = None
):
    """
    Merge a single candle into a specified timeframe, adjusting high, low, and complete status.
    Args:
        candle (Candle): The Candle object to merge.
        timeframe (Timeframe): The target timeframe for merging the candle.
        prev_candle (Candle | None): The previous merged candle, if any.
    Returns:
        tuple[Candle, Candle]: A tuple containing the merged candle and the previous candle.
    """
    if timeframe.ms < candle.timeframe.ms:
        raise ValueError(
            f"Cannot merge candle with timeframe {candle.timeframe} into smaller timeframe {timeframe}"
        )
    
    if prev_candle is None:
        prev_candle = candle.copy(
            timeframe=timeframe,
            timestamp=candle.timestamp - candle.timeframe.ms
        )
    prev_candle = morph_prev_timeseries_obj(candle, prev_candle)

    if time_passed_interval_start(candle.timestamp, timeframe.ms) == 0:
        merged = candle.copy(
            base_timeframe=candle.base_timeframe,
            timeframe=timeframe,
            complete=True if candle.timeframe == timeframe else False
        )
    else:
        merged = prev_candle.copy(
            base_timeframe=candle.base_timeframe,
            timeframe=timeframe,
            timestamp=candle.timestamp,
            close=candle.close,
            high=candle.high if prev_candle.high < candle.high else prev_candle.high,
            low=candle.low if prev_candle.low > candle.low else prev_candle.low,
            complete=True if (
                time_passed_interval_start(candle.timestamp, timeframe.ms)
                + candle.timeframe.ms
                == timeframe.ms
            ) else False
        )
    return merged


def calculate_rsi(
    candle: Candle,
    prev_rsi: RSI | None = None
):
    if prev_rsi is None:
        prev_rsi = RSI(
            base_timeframe=candle.base_timeframe,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp - candle.timeframe.ms
        )
    prev_rsi = morph_prev_timeseries_obj(candle, prev_rsi)

    # defaults
    rsi_value = prev_rsi.value
    avg_gain = prev_rsi.avg_gain
    avg_loss = prev_rsi.avg_loss

    if prev_rsi.price > 0:
        price_change = candle.close - prev_rsi.price
        gain = price_change if price_change > 0 else 0
        loss = -price_change if price_change < 0 else 0
        avg_gain = (prev_rsi.avg_gain * (prev_rsi.length - 1) + gain) / prev_rsi.length
        avg_loss = (prev_rsi.avg_loss * (prev_rsi.length - 1) + loss) / prev_rsi.length
        rsi_value = 100 - 100 / (1 + avg_gain / avg_loss if avg_loss != 0 else 1)
 
    if candle.complete:
        rsi = prev_rsi.copy(
            base_timeframe=candle.base_timeframe,
            timestamp=candle.timestamp,
            value=round(rsi_value, 2),
            price=candle.close,
            avg_gain=avg_gain,
            avg_loss=avg_loss,
            length=prev_rsi.length + 1 if prev_rsi.length < prev_rsi.max_length else prev_rsi.max_length,
            complete=candle.complete
        )
    else:
        rsi = prev_rsi.copy(
            base_timeframe=candle.base_timeframe,
            timestamp=candle.timestamp,
            value=round(rsi_value, 2),
            avg_gain=avg_gain,
            avg_loss=avg_loss,
            complete=candle.complete
        )

    return rsi
