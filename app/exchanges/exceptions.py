class ExchangeException(Exception):
    pass


class PairNotExistsException(ExchangeException):
    pass


class NoTokenException(ExchangeException):
    pass


class APIErrorException(ExchangeException):
    pass


class APIChangedException(ExchangeException):
    pass
