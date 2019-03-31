from datetime import datetime
from decimal import Decimal
from typing import Tuple

import requests
from cached_property import cached_property
from jsonschema import validate, ValidationError

from .base import Exchange, PairData, Pair, ECurrency
from .exceptions import PairNotExistsException, APIErrorException


class BxInThExchange(Exchange):
    """
    https://bx.in.th/info/api/
    """
    name = '[bx.in.th](https://bx.in.th/ref/s9c3HU/)'

    @cached_property
    def _get_data(self) -> dict:
        try:
            response = requests.get('https://bx.in.th/api/')
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            schema = {
                "type": "object",
                "patternProperties": {
                    r"^\d+$": {
                        "type": "object",
                        "properties": {
                            "primary_currency": {"type": "string"},
                            "secondary_currency": {"type": "string"},
                            "last_price": {"type": "number"},
                        },
                        "required": [
                            "primary_currency",
                            "secondary_currency",
                            "last_price",
                        ]
                    },
                    "not": {"required": [""]}
                },
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        result = {}
        for x in data.values():
            # reverse
            to_currency, from_currency = x['primary_currency'], x['secondary_currency']
            result[Pair(ECurrency(from_currency), ECurrency(to_currency))] = x['last_price']

        return result

    @cached_property
    def list_pairs(self) -> Tuple[Pair]:
        return tuple(self._get_data.keys())

    @cached_property
    def list_currencies(self) -> Tuple[ECurrency]:
        currencies = set()

        for from_currency, to_currency in self.list_pairs:
            currencies.add(from_currency)
            currencies.add(to_currency)

        return tuple(currencies)

    def get_pair_info(self, pair: Pair) -> PairData:
        if not self.is_pair_exists(pair):
            raise PairNotExistsException(pair)

        pair_data = self._get_data[pair]

        return PairData(
            pair=pair,
            rate=Decimal(str(pair_data)),
            last_trade_at=datetime.utcnow(),
        )
