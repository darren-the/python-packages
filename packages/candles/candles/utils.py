import datetime
from candles.types import Candle
from candles.globals import BASE_INITIAL_TIMESTAMP


def datetime_to_timestamp(dt: datetime.datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return int(dt.timestamp() * 1000)


def datestr_to_timestamp(date_str: str) -> int:
    """
    Args:
        date_str (str): A date string in the format YYYY-MM-DD
    
    Returns:
        int: a timestamp conversion of the given date string in UTC
    """
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    return datetime_to_timestamp(dt)


def dateobj_to_timestamp(dt_obj: int | datetime.datetime | str) -> int:
    if isinstance(dt_obj, datetime.datetime):
        return datetime_to_timestamp(dt_obj)
    elif isinstance(dt_obj, str):
        return datestr_to_timestamp(dt_obj)
    elif isinstance(dt_obj, int):
        return dt_obj
    else:
        raise ValueError(f"dt_obj has invalid format: {str(dt_obj)}")


def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp / 1000, tz=datetime.timezone.utc)


def validate_candle(candle: Candle, prev_candle: Candle):
    """
    Validate a Candle object to ensure it has a valid timestamp and is of the correct type.
    Args:
        candle (Candle): The Candle object to validate.
        prev_candle (Candle): The previous Candle object for timestamp comparison.
    Raises:
        TypeError: If the candle is not an instance of Candle.
        ValueError: If the candle's timestamp is not greater than the previous candle's timestamp,
            or if the candle's timestamp is before the base initial timestamp.
    """
    if not isinstance(candle, Candle):
        raise TypeError(f"Expected a Candle object, got {type(candle).__name__}")
    if prev_candle is not None and candle.timestamp - prev_candle.timestamp <= 0:
        raise ValueError(
            f"Candle timestamp {candle.timestamp} is not greater than the last candle's timestamp {prev_candle.timestamp}"
        )
    if candle.timestamp < BASE_INITIAL_TIMESTAMP:
        raise ValueError(
            f"Candle timestamp {candle.timestamp} is before the base initial timestamp {BASE_INITIAL_TIMESTAMP}"
        )


def round_down_to_nearest_interval(timestamp: int, interval: int) -> int:
    """Round down a timestamp to the nearest interval."""
    return timestamp - time_passed_interval_start(timestamp, interval)
    # OR THIS???
    # return timestamp - (timestamp % interval)
    # TODO unit test to make sure this is right


def time_passed_interval_start(timestamp: int, interval: int) -> int:
    """Calculate the completed time in the given interval."""
    return (timestamp - BASE_INITIAL_TIMESTAMP) % interval
