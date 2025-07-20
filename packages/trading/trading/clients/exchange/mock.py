from trading.clients.exchange.base import BaseClient
from trading.types import OrderType, Symbol, OrderResponse


class MockClient(BaseClient):
    """
    A mock client for testing purposes that simulates interaction with an exchange.
    This client does not make actual API calls but provides a structure for testing.
    """

    def __init__(self):
        super().__init__()

    @property
    def url(self):
        return "https://mock-exchange.com/api"

    def _submit_order(
        self,
        type: OrderType,
        symbol: Symbol,
        amount: float,
        price: float,
        **kwargs
    ) -> OrderResponse:
        """
        Simulates submitting an order to the exchange.
        Returns a mock OrderResponse object.
        """
        return OrderResponse(
            mts=kwargs.get("mts", 0),
            data=[{"type": type, "symbol": symbol, "amount": amount, "price": price}],
            status="submitted",
            text="Order submitted successfully."
        )