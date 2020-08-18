import logging
from datetime import datetime
from decimal import Decimal
from typing import Tuple

import requests
from cached_property import cached_property
from jsonschema import ValidationError, validate

from app.exchanges.base import ECurrency, Exchange, Pair, PairData
from app.exchanges.exceptions import APIErrorException, PairNotExistsException


class SpTodayExchange(Exchange):
    """
    https://www.sp-today.com
    """

    name = "sp-today"

    @cached_property
    def _get_data(self) -> dict:
        try:
            response = requests.get("https://sp-today.com/app_api/cur_aleppo.json")
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "bid": {"type": "string"},
                        "ask": {"type": "string"},
                    },
                    "required": ["name", "bid", "ask"],
                },
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        result = {}
        for x in data:
            result[Pair(ECurrency(x["name"]), ECurrency("SYP"))] = x

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

        mid = (Decimal(pair_data["ask"]) + Decimal(pair_data["bid"])) / Decimal("2")

        return PairData(pair=pair, rate=mid, last_trade_at=datetime.utcnow())
