from datetime import datetime
from decimal import Decimal, DecimalException

import requests
from cached_property import cached_property
from jsonschema import validate, ValidationError

from .base import Exchange, PairData
from .exceptions import PairNotExistsException, APIErrorException, APIChangedException


class BitfinexExchange(Exchange):
    """
    https://docs.bitfinex.com
    """
    db_id = 1

    @cached_property
    def _get_pairs(self):
        try:
            response = requests.get('https://api.bitfinex.com/v1/symbols')
            response.raise_for_status()
            pairs = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            schema = {
                "type": "array",
                "items": {"type": "string"}
            }
            validate(pairs, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        return tuple(map(lambda x: x.upper(), pairs))

    @cached_property
    def list_pairs(self) -> tuple:
        return self._get_pairs

    @cached_property
    def list_currencies(self) -> tuple:
        currencies = set()

        for x in self.list_pairs:
            first_currency, second_currency = x[:3], x[3:]

            if len(second_currency) != 3:
                raise APIChangedException('Not only 3-symbol currency')

            currencies.add(first_currency)
            currencies.add(second_currency)

        return tuple(currencies)

    def get_pair_info(self, first_currency: str, second_currency: str) -> PairData:
        pair = f'{first_currency}{second_currency}'

        if not self.is_pair_exists(pair):
            raise PairNotExistsException(pair)

        try:
            response = requests.get(f'https://api.bitfinex.com/v1/pubticker/{pair.lower()}')
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            schema = {
                "type": "object",
                "properties": {
                    "mid": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
                "required": [
                    "mid",
                    "timestamp",
                ]
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        try:
            rate = Decimal(data['mid'])
            last_trade_at = float(data['timestamp'])
        except (DecimalException, ValueError) as e:
            raise APIErrorException(e)

        return PairData(
            first_currency=first_currency,
            second_currency=second_currency,
            rate=rate,
            rate_open=None,
            last_trade_at=datetime.fromtimestamp(last_trade_at)
        )
