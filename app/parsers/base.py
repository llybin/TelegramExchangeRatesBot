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

    def __init__(self, text: str, chat_id: int, locale: str, default_currency: str, default_currency_position: bool):
        self.text = text
        self.chat_id = chat_id
        self.default_currency = default_currency
        self.default_currency_position = default_currency_position

        locale_parts = locale.split('-')
        len_parts = len(locale_parts)
        # site-packages/babel/locale-data
        if len_parts == 1:
            # zh
            self.locale = locale_parts[0]
        elif len_parts == 2:
            # zh-hans -> zh_Hans
            self.locale = f'{locale_parts[0].lower()}_{locale_parts[1].capitalize()}'
        elif len_parts == 3:
            # zh-hans-sg -> zh_Hans_SG
            self.locale = f'{locale_parts[0].lower()}_{locale_parts[1].capitalize()}_{locale_parts[2].upper()}'

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def parse(self) -> PriceRequest:
        pass
