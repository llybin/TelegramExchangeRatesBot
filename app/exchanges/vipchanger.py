import logging
from datetime import datetime
from decimal import Decimal
from typing import Tuple

import bs4
import requests
from cached_property import cached_property
from suite.conf import settings

from .base import Exchange, PairData, Pair, ECurrency
from .exceptions import PairNotExistsException, APIErrorException, APIChangedException

MAPPING_CURRENCIES = {
    'Руб': 'RUB',
    'Бат': 'THB',
    'WMR': 'RUB',
    'WMZ': 'USD',
    'Грн': 'UAH',
    'Тенге': 'KZT'
}


class VipChangerExchange(Exchange):
    """
    https://vipchanger.com/
    """
    name = '[vipchanger.com](https://vipchanger.com/?pid=4503)'
    included_reversed_pairs = True

    @cached_property
    def _get_data(self) -> dict:
        try:
            response = requests.get(
                'https://vipchanger.com/',
                proxies=settings.PROXIES_TH)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIErrorException(e)

        pairs = {}

        s = bs4.BeautifulSoup(response.content, features="html.parser")
        table = s.find('table', attrs={'class': 'table_obmen', 'cellspacing': '2'})
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) != 9:
                raise APIChangedException('Format was changed')

            one0 = cells[0].find(text=True)
            one1 = cells[4].find(text=True)

            if not ((one0 == '1 ' or one1 == '1 ') and one0 != one1):
                raise APIChangedException('Format was changed')

            c0 = cells[2].find(text=True)
            c1 = cells[6].find(text=True)
            val = cells[8].find(text=True)

            from_currency = MAPPING_CURRENCIES.get(c0)
            to_currency = MAPPING_CURRENCIES.get(c1)

            if not (from_currency and to_currency):
                logging.warning('Unknown currency: %s %s', c0, c1)
                continue

            pair = Pair(ECurrency(from_currency), ECurrency(to_currency))

            value = Decimal('1') / Decimal(val) if one1 else Decimal(val)

            if pair not in pairs:
                pairs[pair] = [value]
            else:
                pairs[pair].append(value)

        # average sources
        for p, l in pairs.items():
            pairs[p] = sum(l) / len(l)

        # reverse pair
        for pair in list(pairs.keys()):
            reverse_pair = Pair(pair.to_currency, pair.from_currency)
            if reverse_pair not in pairs:
                pairs[reverse_pair] = 1 / pairs[pair]

        return pairs

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

        return PairData(
            pair=pair,
            rate=self._get_data[pair],
            last_trade_at=datetime.utcnow(),
        )
