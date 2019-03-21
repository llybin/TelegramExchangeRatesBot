from datetime import datetime
from decimal import Decimal
from typing import Tuple

import requests
from cached_property import cached_property
from jsonschema import validate, ValidationError
from suite.conf import settings

from .base import Exchange, PairData, Pair, Currency
from .exceptions import PairNotExistsException, APIErrorException, NoTokenException, APIChangedException


class FixerExchange(Exchange):
    """
    https://fixer.io

    Free Plan provides hourly updates up to 1,000 requests/month.
    """
    name = 'Fixer'

    @cached_property
    def _get_data(self) -> dict:
        if not settings.FIXER_TOKEN:
            raise NoTokenException

        try:
            response = requests.get(
                f'http://data.fixer.io/api/latest?access_key={settings.FIXER_TOKEN}')
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            schema = {
                "type": "object",
                "properties": {
                    "base": {"type": "string"},
                    "timestamp": {"type": "number"},
                    "rates": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {"type": "number"},
                        },
                        "not": {"required": [""]}
                    },
                },
                "required": [
                    "base",
                    "timestamp",
                    "rates",
                ]
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        if data['base'] != 'EUR':
            raise APIChangedException('Base currency is not EUR')

        return data

    @cached_property
    def list_pairs(self) -> Tuple[Pair]:
        currencies = self._get_data['rates'].keys()
        base_currency = self._get_data['base'].upper()

        return tuple(Pair(Currency(base_currency), Currency(x.upper())) for x in currencies)

    @cached_property
    def list_currencies(self) -> Tuple[Currency]:
        currencies = self._get_data['rates'].keys()
        base_currency = self._get_data['base'].upper()

        return (Currency(base_currency),) + tuple(Currency(x.upper()) for x in currencies)

    def get_pair_info(self, pair: Pair) -> PairData:
        if not self.is_pair_exists(pair):
            raise PairNotExistsException(pair)

        return PairData(
            pair=pair,
            rate=Decimal(str(self._get_data['rates'][pair.to_currency.code])),
            last_trade_at=datetime.fromtimestamp(self._get_data['timestamp'])
        )
