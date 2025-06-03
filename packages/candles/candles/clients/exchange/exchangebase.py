import time
import datetime
from typing import Generator
from abc import abstractmethod
from candles.types import Candle
from candles.utils import dateobj_to_timestamp, validate_candle


class Client:
    """
    A base class for interacting with an exchange to fetch candlestick 
    data (candles) and process them. This class provides methods for fetching batches 
    of candles, cleaning and filling missing data, and constructing API URLs. It is 
    intended to be subclassed for specific exchange implementations.
    """

    req_limit_per_min: int | None = None

    def __init__(self, interval: int):
        self._interval = interval

    @property
    @abstractmethod
    def url(self):
        """
        Constructs the URL for fetching candle data from the API of the exchange.
        Returns:
            str: The formatted URL string for the API endpoint of the exchange.
        """
        raise NotImplementedError(f"{self.url.__name__} is not implemented.")

    @abstractmethod
    def fetch_raw_candles(self, start: int, end: int) -> Generator[Candle, None, None]:
        """
        Fetches candlestick data for a specified time range.

        Args:
            start (int): The start timestamp in milliseconds.
            end (int): The end timestamp in milliseconds.

        Yields:
            Generator[Candle]: A list of Candle objects representing the candlestick data.
        """
        raise NotImplementedError(f"{self.fetch_raw_candles.__name__} is not implemented.")

    def fetch_candles(
        self,
        start: int | datetime.datetime | str,
        end: int | datetime.datetime | str
    ) -> Generator[Candle, None, None]:
        """
        Fetches batches of candlestick data (candles) within a specified time range.

        This method retrieves candlestick data in batches, adhering to the request 
        limit per minute defined by the exchange.

        Args:
            start (int | datetime.datetime | str): The start time of the range to fetch 
                candles for. Can be provided as a timestamp (int), a datetime object, 
                or an ISO 8601 formatted string.
            end (int | datetime.datetime | str): The end time of the range to fetch 
                candles for. Can be provided as a timestamp (int), a datetime object, 
                or an ISO 8601 formatted string.

        Yields:
            Candle: A generator that yields cleaned candlestick data objects.
        """
        start = dateobj_to_timestamp(start)
        end = dateobj_to_timestamp(end)
        batches = (
            (i, min(i + self.req_limit_per_min * self._interval, end - self._interval))
            for i in range(start, end - self._interval, self.req_limit_per_min * self._interval)
        )
        prev_candle = None
        for batch_start, batch_end in batches:
            for candle in self.fetch_raw_candles(batch_start, batch_end):
                if prev_candle is None:
                    pass
                elif prev_candle.timestamp == candle.timestamp:
                    continue
                elif candle.timestamp - prev_candle.timestamp > self._interval:
                    yield from self.impute_candles(candle, prev_candle)
                else:
                    pass
                validate_candle(candle, prev_candle)
                prev_candle = candle
                yield candle
            time.sleep(60 / self.req_limit_per_min)
    
    def impute_candles(self, candle: Candle, prev_candle: Candle) -> Generator[Candle, None, None]:
        """
        Generates missing candles between the previous candle and the current candle.
        This method creates new Candle objects for each missing interval between the
        previous candle and the current candle.
        Args:
            candle (Candle): The current candle.
            prev_candle (Candle): The previous candle.
        Yields:
            Candle: A new Candle object for each missing interval.
        """
        if candle.timestamp - prev_candle.timestamp <= self._interval:
            raise ValueError(
                f"Current candle timestamp {candle.timestamp} is not greater than "
                f"previous candle timestamp {prev_candle.timestamp} by at least "
                f"the interval {self._interval}."
            )
        for t in range(prev_candle.timestamp + self._interval, candle.timestamp, self._interval):
            last_copy = prev_candle.copy(timestamp=t)
            validate_candle(last_copy, prev_candle)
            yield last_copy
