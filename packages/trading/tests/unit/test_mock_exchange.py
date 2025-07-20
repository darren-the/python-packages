import pytest
from trading.mock_exchange.engine import TradeEngine
from trading.types import Order, OrderStatus, Symbol, OrderType, BalanceType


@pytest.fixture
def basic_engine():
    return TradeEngine(initial_exchange_balance=100000, initial_margin_balance=100000)


@pytest.fixture
def buy_order():
    return Order(
        id=0,
        symbol=Symbol.BTCUSD,
        price=30000,
        quantity=1.0,
        status=OrderStatus.ACTIVE,
        order_type=OrderType.LIMIT,
        mts_create=1,
        mts_update=1
    )


@pytest.fixture
def sell_order():
    return Order(
        id=1,
        symbol=Symbol.BTCUSD,
        price=40000,
        quantity=-1.0,
        status=OrderStatus.ACTIVE,
        order_type=OrderType.LIMIT,
        mts_create=2,
        mts_update=2
    )


def test_add_order(basic_engine: TradeEngine, buy_order: Order):
    basic_engine.add_order(buy_order)
    assert buy_order.id in basic_engine.orders
    assert basic_engine.order_history[-1] == buy_order


def test_remove_order(basic_engine: TradeEngine, buy_order: Order):
    basic_engine.add_order(buy_order)
    canceled = basic_engine.remove_order(buy_order.id, mts=2)

    assert canceled.status == OrderStatus.CANCELED
    assert canceled.mts_update == 2
    assert buy_order.id not in basic_engine.orders
    assert canceled in basic_engine.order_history


def test_trigger_buy_order(basic_engine: TradeEngine, buy_order: Order):
    basic_engine.add_order(buy_order)
    basic_engine.price[Symbol.BTCUSD] = 29000  # simulate previous price

    result = basic_engine.update_price(Symbol.BTCUSD, 31000, mts=3)

    assert result["triggered_orders"][0]["id"] == buy_order.id
    assert buy_order.id not in basic_engine.orders
    assert basic_engine.balance[BalanceType.MARGIN] == 70030.0


def test_trigger_sell_order(basic_engine: TradeEngine, sell_order: Order):
    basic_engine.add_order(sell_order)
    basic_engine.price[Symbol.BTCUSD] = 31000  # simulate previous price

    result = basic_engine.update_price(Symbol.BTCUSD, 40000, mts=2)

    assert result["triggered_orders"][0]["id"] == sell_order.id
    assert sell_order.id not in basic_engine.orders
    assert basic_engine.balance[BalanceType.MARGIN] == 139960.0


def test_trigger_order_requires_prev_price(basic_engine: TradeEngine, buy_order: Order):
    basic_engine.add_order(buy_order)
    # No previous price set

    with pytest.raises(RuntimeError):
        basic_engine.update_price(Symbol.BTCUSD, 31000, mts=3)


def test_invalid_order_type_raises(basic_engine: TradeEngine):
    invalid_order = Order(
        id="bad-order",
        symbol=Symbol.BTCUSD,
        price=1000,
        quantity=1,
        status=OrderStatus.ACTIVE,
        order_type="UNKNOWN",  # not part of OrderType Enum
        mts_create=1,
        mts_update=1
    )

    with pytest.raises(ValueError, match="Unkown order type"):
        basic_engine.update_balance_with_order(invalid_order)
