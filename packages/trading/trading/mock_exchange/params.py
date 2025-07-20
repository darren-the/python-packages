from pydantic import BaseModel, model_validator
from trading.types import Symbol, OrderType, BalanceType


class OrderParams(BaseModel):
    symbol: Symbol
    amount: float
    price: float
    order_type: OrderType
    mts: int = 0


class CancelParams(BaseModel):
    id: int
    mts: int = 0

class UpdatePriceParams(BaseModel):
    symbol: Symbol
    price: float
    mts: int = 0


class DepositParams(BaseModel):
    amount: float
    balance_type: BalanceType

    @model_validator(mode="after")
    def amount_greater_than_zero(self):
        if self.amount < 0:
            raise ValueError(
                f"amount must be greater than or equal to zero. Received {self.amount}."
            )
        return self
