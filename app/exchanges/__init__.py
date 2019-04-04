from .bittrex import BittrexExchange
from .bitfinex import BitfinexExchange
from .openexchangerates import OpenExchangeRatesExchange
from .fixer import FixerExchange
from .bx_in_th import BxInThExchange
from .sp_today import SpTodayExchange
from .vipchanger import VipChangerExchange

__all__ = [
    'BitfinexExchange',
    'BittrexExchange',
    'OpenExchangeRatesExchange',
    'FixerExchange',
    'BxInThExchange',
    'SpTodayExchange',
    'VipChangerExchange',
]
