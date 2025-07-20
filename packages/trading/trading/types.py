from enum import Enum
from dataclasses import dataclass


class OrderType(str, Enum):
    """
    Enum representing different types of orders.
    """
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP LIMIT"
    STOP = "STOP"
    EXCHANGE_LIMIT = "EXCHANGE LIMIT"
    EXCHANGE_MARKET = "EXCHANGE MARKET"
    EXCHANGE_STOP = "EXCHANGE STOP"
    EXCHANGE_STOP_LIMIT = "EXCHANGE STOP LIMIT"


class OrderStatus(str, Enum):
    """
    Enum representing different statuses of an order.
    """
    ACTIVE = "ACTIVE"
    EXECUTED = "EXECUTED"
    CANCELED = "CANCELED"
    PARTIALLY_FILLED = "PARTIALLY FILLED"


class Symbol(str, Enum):
    """
    Enum representing different trading pair symbols.
    """
    BTCUSD = "BTCUSD"
    ETHUSD = "ETHUSD"

    def __str__(self):
        return self.value


class OrderNotifStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    FAILURE = "FAILURE"

    def __str__(self):
        return self.value


class BalanceType(str, Enum):
    EXCHANGE = "EXCHANGE"
    MARGIN = "MARGIN"

    def __str__(self):
        return self.value
    

@dataclass
class Order:
    """
    Dataclass representing an order.
    """
    id: int
    symbol: Symbol
    mts_create: int
    mts_update: int
    quantity: float
    order_type: OrderType
    price: float
    status: OrderStatus

    