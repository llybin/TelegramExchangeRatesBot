import re

from .regex_parser import RegexParser

REPLACES = (
    ('GOLD', 'XAU'),
    ('SILVER', 'XAG'),

    ('IRAQ', 'IQD'),

    ('£', 'GBP'),
    ('$', 'USD'),
    ('DOLLAR', 'USD'),
    ('ДОЛЛАР', 'USD'),
    ('ДОЛАР', 'USD'),
    ('ДОЛЛАРОВ', 'USD'),
    ('ДОЛАРОВ', 'USD'),

    ('€', 'EUR'),
    ('EURO', 'EUR'),
    ('ЕВРО', 'EUR'),

    ('฿', 'THB'),
    ('BHT', 'THB'),
    ('BAHT', 'THB'),
    ('БАТ', 'THB'),
    ('БАТА', 'THB'),
    ('БАТОВ', 'THB'),

    ('BITCOIN', 'BTC'),
    ('LITECOIN', 'LTC'),

    ('₽', 'RUB'),
    ('RUR', 'RUB'),
    ('RUS', 'RUB'),
    ('RUBL', 'RUB'),
    ('РУБЛЬ', 'RUB'),
    ('РУБЛЕЙ', 'RUB'),
    ('РУБЛЯ', 'RUB'),

    ('BLR', 'BYN'),

    ('SUM', 'UZS'),
    ('SOM', 'UZS'),

    ('¥', 'CNY'),
    ('RMB', 'CNY'),
    ('CNH', 'CNY'),
    ('CN¥', 'CNY'),

    ('₴', 'UAH'),
    ('GRN', 'UAH'),
    ('UKR', 'UAH'),
    ('GRV', 'UAH'),
    ('ГРН', 'UAH'),
    ('HRN', 'UAH'),
    ('GRIVNA', 'UAH'),
    ('ГРИВНА', 'UAH'),
    ('ГРИВЕН', 'UAH'),
    ('HRYVNIA', 'UAH'),
    ('HRYVNYA', 'UAH'),

    ('₩', 'KRW'),
    ('WON', 'KRW'),
)


class ExtendRegexParser(RegexParser):
    name = 'ExtendRegexParser'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = self.text.upper()
        for orig, correct in REPLACES:
            self.text = self.text.replace(orig, correct)
