class ConverterException(Exception):
    pass


class NoRatesException(ConverterException):
    pass


class OverflowException(ConverterException):
    pass
