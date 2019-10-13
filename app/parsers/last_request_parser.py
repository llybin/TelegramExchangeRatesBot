"""
Last request parser, when user send only amount

"""

import re

from babel.core import Locale

from app.models import ChatRequests
from suite.database import Session

from .base import DirectionWriting, Parser, PriceRequest
from .exceptions import WrongFormatException
from .regex_parser import parse_amount

# len("123,456,789,012.123456789012") == 28
AMOUNT_PATTERN = r"^[\d\.,\'\s]{1,28}$"
AMOUNT_PATTERN_COMPILED = re.compile(AMOUNT_PATTERN)


class LastRequestParser(Parser):
    name = "LastRequestParser"

    def parse(self) -> PriceRequest:
        text = self.text

        obj = AMOUNT_PATTERN_COMPILED.match(text)
        if not obj:
            raise WrongFormatException

        amount = obj[0]

        if amount:
            amount = parse_amount(amount, self.locale)

        last_request = (
            Session.query(ChatRequests)
            .filter_by(chat_id=self.chat_id)
            .order_by(ChatRequests.modified_at.desc())
            .first()
        )

        if not last_request:
            raise WrongFormatException

        locale = Locale(self.locale)

        if locale.character_order == "right-to-left":
            direction_writing = DirectionWriting.RIGHT2LEFT
        else:
            direction_writing = DirectionWriting.LEFT2RIGHT

        return PriceRequest(
            amount=amount,
            currency=last_request.from_currency.code,
            to_currency=last_request.to_currency.code,
            parser_name=self.name,
            direction_writing=direction_writing,
        )
