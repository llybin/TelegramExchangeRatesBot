from datetime import datetime
from decimal import Decimal
from typing import Tuple

import requests
from cached_property import cached_property
from jsonschema import ValidationError, validate

from app.exchanges.base import ECurrency, Exchange, Pair, PairData
from app.exchanges.exceptions import APIErrorException, PairNotExistsException


class SatangExchange(Exchange):
    """
    https://docs.satang.pro/apis
    """

    name = "[satang.pro](https://satang.pro/signup?referral=STZ3EEU2)"

    @cached_property
    def _get_data(self) -> dict:
        try:
            response = requests.get("https://api.tdax.com/api/orderbook-tickers/")
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise APIErrorException(e)

        try:
            # TODO: [bid][price] [ask][price]
            schema = {
                "type": "object",
                "patternProperties": {
                    r"^.*_.*$": {
                        "type": "object",
                        "properties": {
                            "bid": {"type": "object"},
                            "ask": {"type": "object"},
                        },
                        "required": ["bid", "ask"],
                    },
                },
            }
            validate(data, schema)
        except ValidationError as e:
            raise APIErrorException(e)

        result = {}
        for currencies, info in data.items():
            from_currency, to_currency = currencies.split("_")

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

        mid = (
            Decimal(str(pair_data["ask"]["price"]))
            + Decimal(str(pair_data["bid"]["price"]))
        ) / Decimal("2")

        low24h = high24h = None

        return PairData(
            pair=pair,
            rate=mid,
            low24h=low24h,
            high24h=high24h,
            last_trade_at=datetime.utcnow(),
        )
