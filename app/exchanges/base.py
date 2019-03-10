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
    volume24h: Decimal or None = None


class Exchange(ABC):
    @property
    @abstractmethod
    def db_id(self) -> int:
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

    @staticmethod
    def reverse_pair(pair: Pair):
        return Pair(pair.to_currency, pair.from_currency)

    @abstractmethod
    def get_pair_info(self, pair: Pair) -> PairData:
        pass
