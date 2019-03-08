from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import NamedTuple


class PairData(NamedTuple):
    first_currency: str
    second_currency: str
    rate: Decimal
    rate_open: Decimal or None
    last_trade_at: datetime


class Exchange(ABC):
    @property
    @abstractmethod
    def db_id(self) -> int:
        pass

    @property
    @abstractmethod
    def list_pairs(self) -> tuple:
        pass

    @property
    @abstractmethod
    def list_currencies(self) -> tuple:
        pass

    def is_pair_exists(self, pair: str) -> bool:
        return pair in self.list_pairs

    def is_currency_exists(self, currency: str) -> bool:
        return currency in self.list_currencies

    @abstractmethod
    def get_pair_info(self, cur0: str, cur1: str) -> PairData:
        pass
