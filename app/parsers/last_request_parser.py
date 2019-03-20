"""
Last request parser, when user send only amount

"""

import re
from pyramid_sqlalchemy import Session

from .base import (
    PriceRequest,
    Parser,
)
from .exceptions import WrongFormatException
from .regex_parser import parse_amount
from ..models import ChatRequests


# len("123,456,789,012.123456789012") == 28
AMOUNT_PATTERN = r'^[\d\.,\'\s]{1,28}$'
AMOUNT_PATTERN_COMPILED = re.compile(AMOUNT_PATTERN)


class LastRequestParser(Parser):
    name = 'LastRequestParser'

    def parse(self) -> PriceRequest:
        text = self.text

        obj = AMOUNT_PATTERN_COMPILED.match(text)
        if not obj:
            raise WrongFormatException

        amount = obj[0]

        if amount:
            amount = parse_amount(amount, self.locale)

        last_request = Session.query(ChatRequests).filter_by(
            chat_id=self.chat_id
        ).order_by(ChatRequests.modified_at.desc()).first()

        if not last_request:
            raise WrongFormatException

        return PriceRequest(
            amount=amount,
            currency=last_request.from_currency.code,
            to_currency=last_request.to_currency.code,
            parser_name=self.name,
            # direction_writing
        )
