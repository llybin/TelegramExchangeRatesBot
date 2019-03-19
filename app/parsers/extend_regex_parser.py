from .regex_parser import RegexParser


class ExtendRegexParser(RegexParser):
    name = 'ExtendRegexParser'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: replace
        self.text = self.text
        """
'GOLD', 'XAU'
'SILVER', 'XAG'

'IRAQ', 'IQD'      # iraq

'£', 'GBP'         # uk

'$', 'USD'         # usa
'DOLLAR', 'USD'    # usa
'ДОЛЛАР', 'USD'    # usa
'ДОЛАР', 'USD'     # usa
'ДОЛЛАРОВ', 'USD'  # usa
'ДОЛАРОВ', 'USD'   # usa

'€', 'EUR'         # europa
'EURO', 'EUR'      # europa
'ЕВРО', 'EUR'      # europa

'฿', 'THB'         # thailand
'BHT', 'THB'       # thailand
'BAHT', 'THB'      # thailand
'БАТ', 'THB'       # thailand
'БАТА', 'THB'      # thailand
'БАТОВ', 'THB'     # thailand

'BITCOIN', 'BTC'
'LITECOIN', 'LTC'

'₽', 'RUB'         # russia
'RUR', 'RUB'       # russia
'RUS', 'RUB'       # russia
'RUBL', 'RUB'      # russia
'РУБЛЬ', 'RUB'     # russia
'РУБЛЕЙ', 'RUB'    # russia
'РУБЛЯ', 'RUB'     # russia

'BLR', 'BYN'       # Belarus

'SUM', 'UZS'       # uzbekistan
'SOM', 'UZS'       # uzbekistan

'¥', 'CNY'         # chine
'RMB', 'CNY'       # chine
'CNH', 'CNY'       # chine
'CN¥', 'CNY'       # chine

'₴', 'UAH'         # ukraine
'GRN', 'UAH'       # ukraine
'UKR', 'UAH'       # ukraine
'GRV', 'UAH'       # ukraine
'ГРН', 'UAH'       # ukraine
'HRN', 'UAH'       # ukraine
'GRIVNA', 'UAH'    # ukraine
'ГРИВНА', 'UAH'    # ukraine
'ГРИВЕН', 'UAH'    # ukraine
'HRYVNIA', 'UAH'   # ukraine
'HRYVNYA', 'UAH'   # ukraine

'₩', 'KRW'         # korean won
'WON', 'KRW'       # korean kpw - north, krw - south
        """
