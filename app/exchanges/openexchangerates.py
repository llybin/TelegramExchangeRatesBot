from datetime import datetime
from decimal import Decimal

import requests
from cached_property import cached_property
from jsonschema import validate, ValidationError
from suite.conf import settings

from .base import Exchange, PairData
from .exceptions import PairNotExistsException, APIErrorException, NoTokenException


class OpenExchangeRatesExchange(Exchange):
    """
    https://openexchangerates.org/
    """
    db_id = 2

    @cached_property
    def _get_data(self):
        if not settings.OPENEXCHANGERATES_TOKEN:
            raise NoTokenException

        try:
            response = requests.get(
                f'http://openexchangerates.org/api/latest.json?app_id={settings.OPENEXCHANGERATES_TOKEN}')
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

        return data

    @cached_property
    def list_pairs(self) -> tuple:
        currencies = self._get_data['rates'].keys()
        base_currency = self._get_data['base']

        return tuple(f'{base_currency}{x}'.upper() for x in currencies)

    @cached_property
    def list_currencies(self) -> tuple:
        currencies = self._get_data['rates'].keys()
        base_currency = self._get_data['base']

        return tuple(currencies) + (base_currency,)

    def get_pair_info(self, first_currency: str, second_currency: str) -> PairData:
        if not self.is_currency_exists(second_currency) or first_currency != self._get_data['base']:
            raise PairNotExistsException(f'{first_currency}{second_currency}')

        return PairData(
            first_currency=first_currency,
            second_currency=second_currency,
            rate=Decimal(str(self._get_data['rates'][second_currency])),
            rate_open=None,
            last_trade_at=datetime.fromtimestamp(self._get_data['timestamp'])
        )
