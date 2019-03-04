class ValidationException(Exception):
    pass


class WrongFormatException(ValidationException):
    pass


class UnknownCurrencyException(ValidationException):
    pass
