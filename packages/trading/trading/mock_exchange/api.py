from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException
from trading.mock_exchange.engine import TradeEngine
from trading.mock_exchange.params import OrderParams, CancelParams, UpdatePriceParams, DepositParams
from trading.mock_exchange.response import OrderResponse
from trading.mock_exchange.utils import create_order_id
from trading.types import Order, OrderStatus, OrderNotifStatus


trade_engine: TradeEngine | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global trade_engine
    trade_engine = TradeEngine()
    yield
    trade_engine = None


app = FastAPI(lifespan=lifespan)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(exc.detail, status_code=exc.status_code)


@app.get("/orders")
def retrieve_orders():
    return trade_engine.get_orders()


@app.get("/orders/hist")
def retrieve_order_history():
    return trade_engine.get_order_history()


@app.post("/order/submit")
def submit_order(params: OrderParams):
    try:
        order = Order(
            id=create_order_id(),
            symbol=params.symbol,
            mts_create=params.mts,
            mts_update=params.mts,
            quantity=params.amount,
            order_type=params.order_type,
            price=params.price,
            status=OrderStatus.ACTIVE
        )
        trade_engine.add_order(order)
        return OrderResponse(
            mts=order.mts_create,
            data=[order],
            status=OrderNotifStatus.SUCCESS,
            text=""
            )
    except:
        raise HTTPException(
            status_code=500,
            detail=OrderResponse(
                mts=-1,
                data=[],
                status=OrderNotifStatus.ERROR,
                text="There was an internal server error. See server logs for details."
            ).model_dump()
        )


@app.post("/orders/cancel")
def cancel_order(params: CancelParams):
    try:
        canceled_order = trade_engine.remove_order(params.id, params.mts)
        return OrderResponse(
            mts=params.mts,
            data=[canceled_order],
            status=OrderNotifStatus.SUCCESS,
            text=""
        )
    except:
        raise HTTPException(
            status_code=500,
            detail=OrderResponse(
                mts=-1,
                data=[],
                status=OrderNotifStatus.ERROR,
                text="There was an internal server error. See server logs for details."
            ).model_dump()
        )


@app.post("/price/update")
def update_price(params: UpdatePriceParams):
    return trade_engine.update_price(params.symbol, params.price, params.mts)


@app.get("/balance")
def get_balance():
    return trade_engine.balance


@app.post("/balance/deposit")
def deposit_balance(params: DepositParams):
    return trade_engine.add_balance(params.amount)
