import pytest


def test_not_implemented():
    with pytest.raises(NotImplementedError):
        from trading.clients.exchange.base import BaseClient
