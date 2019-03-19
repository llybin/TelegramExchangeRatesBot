from abc import ABC, abstractmethod
from decimal import Decimal
from typing import NamedTuple


class DirectionWriting(object):
    UNKNOWN = None
    LEFT2RIGHT = 'LEFT2RIGHT'
    RIGHT2LEFT = 'RIGHT2LEFT'


class PriceRequest(NamedTuple):
    amount: Decimal or None
    currency: str
    to_currency: str or None
    parser_name: str
    direction_writing: DirectionWriting = DirectionWriting.UNKNOWN


class Parser(ABC):
    text: str

    def __init__(self, text: str, locale: str, default_currency: str, default_currency_position: bool):
        self.text = text
        self.locale = locale
        self.default_currency = default_currency
        self.default_currency_position = default_currency_position

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def parse(self) -> PriceRequest:
        pass
