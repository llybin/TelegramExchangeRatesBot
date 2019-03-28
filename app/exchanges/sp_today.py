import logging
from datetime import datetime
from decimal import Decimal
from typing import Tuple

import requests
from cached_property import cached_property
from jsonschema import validate, ValidationError

from .base import Exchange, PairData, Pair, ECurrency
from .exceptions import PairNotExistsException, APIErrorException

MAPPING_CURRENCIES = {
    "dollar": "USD",
    "euro": "EUR",
    "tl": "TRY",
    "eg": "EGP",
    "sa": "SAR",
    "jd": "JOD",
    "ed": "AED",
    "qar": "QAR",
    "bhd": "BHD",
    "lyd": "LYD",
    "kd": "KWD",
    "omr": "OMR",
    "uk": "GBP",
    "sek": "SEK",
    "cad": "CAD",
    "nok": "NOK",
    "dkk": "DKK",
}


class SpTodayExchange(Exchange):
    """
    https://www.sp-today.com

    https://www.sp-today.com/ticker-news/aleppo_cur.json
    https://sp-today.com/ticker-news/cur.json
    https://sp-today.com/fcur/fcur2.json
    """
    name = 'sp-today'

    @cached_property
    def _get_data(self) -> dict:
        try:
            response = requests.get('http://www.sp-today.com/ticker-news/aleppo_cur.json')
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            # TODO: check and bitfinex also array
            schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "sell_price": {"type": "string"},
                        "buy_price": {"type": "string"},
                    },
                    "required": [
                        "name",
                        "sell_price",
                        "buy_price",
                    ]
                }
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        result = {}
        for x in data:
            if x['name'] not in MAPPING_CURRENCIES:
                logging.warning('New currency added: %s', x['name'])
                continue

            result[Pair(ECurrency(MAPPING_CURRENCIES[x['name']]), ECurrency('SYP'))] = x

        if len(result) != len(MAPPING_CURRENCIES):
            logging.warning('Currencies were deleted: %s', set(MAPPING_CURRENCIES.keys() - set(result.keys())))

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

        mid = (Decimal(pair_data['sell_price']) + Decimal(pair_data['buy_price'])) / Decimal('2')

        return PairData(
            pair=pair,
            rate=mid,
            last_trade_at=datetime.utcnow(),
        )
