import json
from dataclasses import dataclass
from enum import Enum
from typing_extensions import Self


class TimeframeUnit(Enum):
    MINUTE = ("m", 60_000)
    HOUR = ("h", 3_600_000)
    DAY = ("D", 86_400_000)
    WEEK = ("W", 604_800_000)

    def __init__(self, label: str, ms: int):
        self.label = label
        self.ms = ms


class Timeframe(str, Enum):
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


@dataclass(frozen=True)
class RSI(TimeseriesObject):
    value: float = 0
    price: float = 0
    avg_gain: float = 0
    avg_loss: float = 0
    length: int = 0
    max_length: int = 14
