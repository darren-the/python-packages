from abc import abstractmethod
from trading.types import OrderType, Symbol, OrderResponse


class BaseClient:
    """
    A base class for interacting with an exchange to make authenticated requests.
    This class is intended to be subclassed for specific exchange implementations.
    """

    req_limit_per_min: int | None = None

    def __init__(self):
        self._reqs_past_min: list[int] = []

    @property
    @abstractmethod
    def url(self):
        """
        Constructs the base URL for the exchange's authenticated endpoints.
        Returns:
            str: The formatted URL string for the API endpoint of the exchange.
        """
        raise NotImplementedError(f"{self.url.__name__} is not implemented.")
    
    @abstractmethod
    def _submit_order(
        self,
        type: OrderType,
        symbol: Symbol,
        amount: float,
        price: float,
        **kwargs
    ) -> OrderResponse:
        """
        Internal method to submit an order to the exchange.
        This method should be implemented by subclasses to handle the specifics of the exchange's API.
        """
        raise NotImplementedError(f"{self._submit_order.__name__} is not implemented.")

    def check_rate_limit(self):
        """
        Checks if the rate limit for requests has been reached.
        """
        if self.req_limit_per_min is not None:
            raise NotImplementedError("I'm too lazy")

    def submit_order(
        self,
        type: OrderType,
        symbol: Symbol,
        amount: float,
        price: float,
        **kwargs
    ) -> OrderResponse:
        """
        Submits an order to the exchange.

        Args:
            type (OrderType): The type of the order (e.g., LIMIT, MARKET).
            symbol (Symbol): The trading pair symbol (e.g., BTCUSD, ETHUSD).
            amount (float): The amount of the asset to trade.
            price (float): The price at which to execute the order.
            **kwargs: Additional parameters for the order.

        Returns:
            OrderResponse: The status of the submitted order.
        """
        
        self.check_rate_limit()
        return self._submit_order(type, symbol, amount, price, **kwargs)
    
