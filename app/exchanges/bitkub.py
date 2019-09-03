import logging
from datetime import datetime
from decimal import Decimal
from typing import Tuple

import requests
from cached_property import cached_property
from jsonschema import validate, ValidationError

from .base import Exchange, PairData, Pair, ECurrency
from .exceptions import PairNotExistsException, APIErrorException
from app.queries import get_all_currency_codes


class BitkubExchange(Exchange):
    """
    https://github.com/bitkub/bitkub-official-api-docs
    """
    name = '[bitkub.com](https://www.bitkub.com/signup?ref=64572)'

    @cached_property
    def _get_data(self) -> dict:
        try:
            response = requests.get('https://api.bitkub.com/api/market/ticker')
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            schema = {
                "type": "object",
                "patternProperties": {
                    r"^.*_.*$": {
                        "type": "object",
                        "properties": {
                            "lowestAsk": {"type": "number"},
                            "highestBid": {"type": "number"},
                            "isFrozen": {"type": "number"},
                            "low24hr": {"type": "number"},
                            "high24hr": {"type": "number"},
                        },
                        "required": [
                            "lowestAsk",
                            "highestBid",
                            "isFrozen",
                            "low24hr",
                            "high24hr",
                        ]
                    },
                    "not": {"required": [""]}
                },
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        result = {}
        all_currency_codes = get_all_currency_codes()
        for currencies, info in data.items():
            if info['isFrozen']:
                logging.info('Bitkub isFrozen: %s', currencies)
                continue

            # reverse
            to_currency, from_currency = currencies.split('_')

            if not info['lowestAsk'] or not info['highestBid']:
                if to_currency in all_currency_codes and from_currency in all_currency_codes:
                    logging.info('Bitkub no Bid Ask: %s', info)
                continue

            result[Pair(ECurrency(from_currency), ECurrency(to_currency))] = info

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

        mid = (Decimal(str(pair_data['lowestAsk'])) + Decimal(str(pair_data['highestBid']))) / Decimal('2')

        if pair_data['low24hr'] and pair_data['high24hr']:
            low24h = Decimal(str(pair_data['low24hr']))
            high24h = Decimal(str(pair_data['high24hr']))
        else:
            low24h = high24h = None

        return PairData(
            pair=pair,
            rate=mid,
            low24h=low24h,
            high24h=high24h,
            last_trade_at=datetime.utcnow(),
        )
