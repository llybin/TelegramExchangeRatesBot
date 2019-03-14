class CurrencyNotSupportedException(Exception):
    pass


class PriceRequesterException(Exception):
    pass


class EmptyPriceRequestException(PriceRequesterException):
    pass
