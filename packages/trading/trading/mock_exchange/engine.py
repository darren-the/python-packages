from dataclasses import asdict
from copy import deepcopy
from trading.types import Order, OrderStatus, Symbol, BalanceType, OrderType


class TradeEngine:
    def __init__(
        self,
        initial_exchange_balance: float = 0,
        initial_margin_balance: float = 0,
        maker_fee: float = 0.001,
        taker_fee: float = 0.002
    ):
        self.orders: dict[str, Order] = {}
        self.order_history: list[Order] = []
        self.price: dict[Symbol, float] = {}
        self.balance = {
            BalanceType.EXCHANGE: initial_exchange_balance,
            BalanceType.MARGIN: initial_margin_balance
        }
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
    
    def add_order(self, order: Order):
        self.orders[order.id] = order
        self.order_history.append(order)

    def get_orders(self):
        return [asdict(order) for order in self.orders.values()]
    
    def get_order_history(self, ascending: bool = True):
        if ascending:
            return self.order_history
        else:
            return reversed(self.order_history)

    def remove_order(self, order_id: int, mts: int):
        if order_id in self.orders:
            canceled_order = deepcopy(self.orders[order_id])
            canceled_order.mts_update = mts
            canceled_order.status = OrderStatus.CANCELED
            self.orders.pop(order_id)
            self.order_history.append(canceled_order)
            return canceled_order

    def update_price(self, symbol: Symbol, price: float, mts: int):
        if len(self.orders) > 0:
            triggered_orders = self._trigger_orders(symbol, price, mts)
        else:
            triggered_orders = []
        self.price[symbol] = price
        return {
            "mts": mts,
            "symbol": symbol,
            "price": price,
            "triggered_orders": [asdict(order) for order in triggered_orders]
        }

    def _trigger_orders(self, symbol: Symbol, price: float, mts: int):
        prev_price = self.price.get(symbol)
        if prev_price == None:
            raise RuntimeError(
                f"Method {self._trigger_orders.__name__} can only be called when a "
                "previous price already exists. Called with "
                f"symbol={symbol} and price={price}, but previous price was None. "
                ""
            )
        triggered_orders = []
        for order in self.orders.values():
            # TODO: this currently does not consider scenario where limit buy order
            # is set above the current price (this should execute immediately as a market buy order)
            if order.symbol == symbol and (
                prev_price <= order.price <= price
                or price <= order.price <= prev_price
            ):
                executed_order = self._execute_order(order.id, mts)
                triggered_orders.append(executed_order)
        for order in triggered_orders:
            self.orders.pop(order.id)
            self.order_history.append(order)
        return triggered_orders
    
    def _execute_order(self, order_id: int, mts: int):
        executed_order = deepcopy(self.orders[order_id])
        executed_order.mts_update = mts
        executed_order.status = OrderStatus.EXECUTED
        self.update_balance_with_order(executed_order)
        return executed_order
    
    def add_balance(self, amount: float, balance_type: BalanceType):
        self.balance[balance_type] += amount
        if self.balance[balance_type] < 0:
            raise RuntimeError(f"Balance went below zero, balance = {self.balance[balance_type]}.")
        return self.balance
    
    def update_balance_with_order(self, order: Order):
        if order.order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT):
            amount = (-1) * order.price * order.quantity * (1 - self.maker_fee)
            self.add_balance(amount, BalanceType.MARGIN)
        elif order.order_type in (OrderType.MARKET, OrderType.STOP):
            amount = (-1) * order.price * order.quantity * (1 - self.taker_fee)
            self.add_balance(amount, BalanceType.MARGIN)
        elif order.order_type in (OrderType.EXCHANGE_LIMIT, OrderType.EXCHANGE_STOP_LIMIT):
            amount = (-1) * order.price * order.quantity * (1 - self.maker_fee)
            self.add_balance(amount, BalanceType.EXCHANGE)
        elif order.order_type in (OrderType.EXCHANGE_MARKET, OrderType.EXCHANGE_STOP):
            amount = (-1) * order.price * order.quantity * (1 - self.taker_fee)
            self.add_balance(amount, BalanceType.EXCHANGE)
        else:
            raise ValueError(f"Unkown order type '{order.order_type}'")
