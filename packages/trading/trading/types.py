from enum import Enum
from dataclasses import dataclass


class OrderType(str, Enum):
    """
    Enum representing different types of orders.
    """
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    EXCHANGE_LIMIT = "EXCHANGE LIMIT"
    EXCHANGE_MARKET = "EXCHANGE MARKET"
    STOP = "STOP"
    EXCHANGE_STOP = "EXCHANGE STOP"


class Symbol(str, Enum):
    """
    Enum representing different trading pair symbols.
    """
    BTCUSD = "BTCUSD"
    ETHUSD = "ETHUSD"

    def __str__(self):
        return self.value


@dataclass
class OrderStatus:
    """
    Dataclass representing the status of an order.
    """
    mts: int
    data: list
    status: str
    text: str
