import re


# TODO: not so good e.g. 00.1 or 00000.1, many first zeros
MONEY_PATTERN_EU = r'((\d{1,3}(\.\d{3}){1,3}|\d{1,12})(,\d{1,8})?)'
MONEY_PATTERN_US = r'((\d{1,3}(,\d{3}){1,3}|\d{1,12})(\.\d{1,8})?)'

MONEY_PATTERN = f'{MONEY_PATTERN_EU}|{MONEY_PATTERN_US}'

CURRENCY_SEPARATORS_LIST = (' to ', ' in ', '=', ' = ', r'\s')
CURRENCY_SEPARATORS_STR = '|'.join(CURRENCY_SEPARATORS_LIST)
CURRENCY_SEPARATORS_PATTERN = re.compile(f'({CURRENCY_SEPARATORS_STR})')


def price_pattern() -> str:
    # left to right, 12USDEUR, 12USD, USDEUR, EUR, ...
    #       (12)?  ?(          USD((  )?          EUR)?)
    l2r = r'(%s)?\s?([a-zA-Z]{3,5}((%s)?[a-zA-Z]{3,5})?)' % (MONEY_PATTERN, CURRENCY_SEPARATORS_STR)

    # right to left, EURUSD12, USD12, EURUSD, EUR, ...
    #       ((          EUR(  )?)?          USD)  ?(12)?
    r2l = r'(([a-zA-Z]{3,5}(%s)?)?[a-zA-Z]{3,5})\s?(%s)?' % (CURRENCY_SEPARATORS_STR, MONEY_PATTERN)

    return f'({l2r}|{r2l})$'


PRICE_PATTERN = re.compile(price_pattern(), re.IGNORECASE)
