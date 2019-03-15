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

    def __init__(self, text):
        self.text = text

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def parse(self) -> PriceRequest:
        pass
