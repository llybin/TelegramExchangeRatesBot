from abc import ABC, abstractmethod
from decimal import Decimal
from typing import NamedTuple

from .number_format import NumberFormat


class DirectionWriting(object):
    UNKNOWN = None
    LEFT2RIGHT = 'LEFT2RIGHT'
    RIGHT2LEFT = 'RIGHT2LEFT'


class PriceRequest(NamedTuple):
    amount: Decimal or None
    currency: str
    to_currency: str or None
    direction_writing: DirectionWriting = DirectionWriting.UNKNOWN
    number_format: NumberFormat = NumberFormat.UNKNOWN


class Parser(ABC):

    def __init__(self, text):
        self.text = text

    @abstractmethod
    def parse(self) -> PriceRequest:
        pass
