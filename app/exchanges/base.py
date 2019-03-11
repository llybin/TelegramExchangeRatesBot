from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import NamedTuple, Tuple


class Currency(NamedTuple):
    code: str

    def __str__(self):
        return self.code


class Pair(NamedTuple):
    from_currency: Currency
    to_currency: Currency


class PairData(NamedTuple):
    pair: Pair
    rate: Decimal
    last_trade_at: datetime
    rate_open: Decimal or None = None
    low24h: Decimal or None = None
    high24h: Decimal or None = None


def reverse_pair(pair: Pair) -> Pair:
    return Pair(pair.to_currency, pair.from_currency)


def reverse_amount(rate: Decimal) -> Decimal or None:
    if not rate:
        return rate

    return Decimal('1') / rate


def reverse_pair_data(pair_data: PairData) -> PairData:
    return PairData(
        pair=reverse_pair(pair_data.pair),
        rate=reverse_amount(pair_data.rate),
        last_trade_at=pair_data.last_trade_at,
        rate_open=reverse_amount(pair_data.rate_open),
        low24h=reverse_amount(pair_data.low24h),
        high24h=reverse_amount(pair_data.high24h),
    )


class Exchange(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def list_pairs(self) -> Tuple[Pair]:
        pass

    @property
    @abstractmethod
    def list_currencies(self) -> Tuple[Currency]:
        pass

    def is_pair_exists(self, pair: Pair) -> bool:
        return pair in self.list_pairs

    def is_currency_exists(self, currency: Currency) -> bool:
        return currency in self.list_currencies

    @abstractmethod
    def get_pair_info(self, pair: Pair) -> PairData:
        pass
