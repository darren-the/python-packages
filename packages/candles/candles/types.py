import json
from dataclasses import dataclass
from enum import Enum
from typing_extensions import Self
from candles.exceptions import CandleValidationError, TimeseriesValidationError
from candles.globals import BASE_INITIAL_TIMESTAMP


class TimeframeUnit(Enum):
    MINUTE = ("m", 60_000)
    HOUR = ("h", 3_600_000)
    DAY = ("D", 86_400_000)
    WEEK = ("W", 604_800_000)

    def __init__(self, label: str, ms: int):
        self.label = label
        self.ms = ms


class Timeframe(str, Enum):
    _1m = "1m"
    _5m = "5m"
    _15m = "15m"
    _1h = "1h"
    _4h = "4h"
    _1D = "1D"
    _1W = "1W"

    def __str__(self):
        return self.value

    @property
    def length(self) -> int:
        return int(self.value[:-1])

    @property
    def unit(self) -> TimeframeUnit:
        unit_str = self.value[-1]
        for unit in TimeframeUnit:
            if unit.label == unit_str:
                return unit
        raise ValueError(f"Unknown unit: {unit_str}")

    @property
    def ms(self) -> int:
        return self.length * self.unit.ms
    
    @classmethod
    def get_min_timeframe(cls) -> 'Timeframe':
        return min(cls, key=lambda tf: tf.ms)


@dataclass(frozen=True)
class TimeseriesObject:
    """
    Base class for timeseries data types.
    """
    base_timeframe: Timeframe
    timeframe: Timeframe
    timestamp: int
    complete: bool = True
    
    def __post_init__(self):
        if not isinstance(self.timestamp, int):
            raise TypeError(f"Timestamp must be an integer, got {type(self.timestamp).__name__}")
        if not isinstance(self.complete, bool):
            raise TypeError(f"Complete flag must be a boolean, got {type(self.complete).__name__}")
        if self.timestamp < 0:
            raise TimeseriesValidationError(f"Timestamp must be non-negative, got {self.timestamp}")
        if self.timestamp < BASE_INITIAL_TIMESTAMP:
            raise TimeseriesValidationError(
                f"Timestamp {self.timestamp} is before the base initial timestamp {BASE_INITIAL_TIMESTAMP}"
            )
        # if self.timestamp % self.timeframe.ms != 0:
        #     raise TimeseriesValidationError(
        #         f"Timestamp {self.timestamp} is not aligned with the timeframe {self.timeframe}"
        #     )

    def __repr__(self):
        return json.dumps(self.__dict__)

    def copy(self, **kwargs) -> Self:
        """
        Create a copy of the timeseries type with updated attributes.
        """
        updated_attrs = {**self.__dict__, **kwargs}
        return type(self)(**updated_attrs)

    @property
    def start_timestamp(self) -> int:
        """
        start_timestamp = timestamp
        """
        return self.timestamp
    
    @property
    def end_timestamp(self) -> int:
        """
        end_timestamp = timestamp + timeframe.ms
        """
        return self.timestamp + self.timeframe.ms


@dataclass(frozen=True)
class Candle(TimeseriesObject):
    open: float = 0
    close: float = 0
    high: float = 0
    low: float = 0


    def __post_init__(self):
        super().__post_init__()
        for price in (self.open, self.close, self.high, self.low):
            if not isinstance(price, (int, float)):
                raise TypeError(f"Price values must be numeric, got {type(price).__name__}")
            if price < 0:
                raise CandleValidationError(f"Candle values must be non-negative, got {price}")
        if not (self.low <= self.open <= self.high and self.low <= self.close <= self.high):
            raise CandleValidationError("Open and close prices must be within the high and low prices.")

@dataclass(frozen=True)
class RSI(TimeseriesObject):
    value: float = 0
    price: float = 0
    avg_gain: float = 0
    avg_loss: float = 0
    length: int = 0
    max_length: int = 14
