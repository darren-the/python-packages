from pydantic import BaseModel
from trading.types import Order, OrderNotifStatus


class OrderResponse(BaseModel):
    """
    Basemodel representing an order response.
    """
    mts: int
    data: list[Order]
    status: OrderNotifStatus
    text: str
