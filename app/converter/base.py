from datetime import datetime
from decimal import Decimal
from typing import NamedTuple

from app.parsers.base import PriceRequest


class PriceRequestResult(NamedTuple):
    price_request: PriceRequest
    exchanges: list
    rate: Decimal
    last_trade_at: datetime
    rate_open: Decimal or None = None
    low24h: Decimal or None = None
    high24h: Decimal or None = None
