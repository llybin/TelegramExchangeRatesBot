# TODO:
# https://en.wikipedia.org/wiki/Indian_numbering_system
# https://en.wikipedia.org/wiki/Decimal_separator
# https://docs.oracle.com/cd/E19455-01/806-0169/overview-9/index.html
# https://docs.microsoft.com/en-us/globalization/locale/number-formatting

# TODO: 12, 12
NUMBER_PATTERN_DOT_SIMPLE = r'(\d{1,12}(\.\d{1,8})?)'
NUMBER_PATTERN_EU = r'((\d{1,3}(\.\d{3}){1,3}|\d{1,12})(,\d{1,8})?)'
# NUMBER_PATTERN_RU = r'((\d{1,3}(\s\d{3}){1,3}|\d{1,12})(,\d{1,8})?)'
NUMBER_PATTERN_US = r'((\d{1,3}(,\d{3}){1,3}|\d{1,12})(\.\d{1,8})?)'

NUMBER_PATTERN_ALL = f'({NUMBER_PATTERN_EU}|{NUMBER_PATTERN_US})'


class NumberFormat(object):
    UNKNOWN = None
    EU = (',', '.')  # 1,000,000,00
    # RU = (' ', ',')  # 1 000 000,00
    US = (',', '.')  # 1,000,000.00
