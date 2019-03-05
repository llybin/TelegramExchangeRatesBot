import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = {
    'url': os.environ.get('DB_URL', 'postgresql://postgres:@db:5432/postgres'),
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')

CURRENCIES = [
    'NIO', 'AFN', 'UYU', 'NPR', 'GYD', 'CAD', 'LYD', 'BZD',
    'FJD', 'SOS', 'BWP', 'ETB', 'MAD', 'JOD', 'BMD', 'RUB',
    'MMK', 'UGX', 'HTG', 'XDR', 'CVE', 'GEL', 'ZWL', 'BIF',
    'LKR', 'BGN', 'CLP', 'VUV', 'RSD', 'SGD', 'MYR',
    'JMD', 'CUP', 'KMF', 'KPW', 'XPF', 'SCR', 'TZS', 'AZN',
    'AUD', 'KHR', 'BOB', 'PKR', 'ARS', 'CZK', 'ANG', 'AOA',
    'KWD', 'XPD', 'KES', 'SBD', 'PHP', 'PGK', 'USD', 'OMR',
    'GBP', 'XAU', 'HNL', 'EUR', 'CLF', 'YER', 'BYR', 'FKP',
    'ZMW', 'WST', 'STD', 'MUR', 'ISK', 'THB', 'BND', 'IRR',
    'IDR', 'SVC', 'QAR', 'NGN', 'BDT', 'MGA', 'CRC', 'NAD',
    'XCD', 'SAR', 'RON', 'IQD', 'KGS', 'AMD', 'SZL', 'ALL',
    'HRK', 'MRO', 'BHD', 'DZD', 'TMT', 'BSD', 'ZAR', 'MNT',
    'UZS', 'TND', 'GHS', 'EGP', 'RWF', 'SYP', 'ERN', 'TOP',
    'TWD', 'CDF', 'MOP', 'MXN', 'BAM', 'XOF', 'VND', 'MKD',
    'MDL', 'AWG', 'SDG', 'KRW', 'PYG', 'XAG', 'COP', 'ILS',
    'PEN', 'JPY', 'PAB', 'PLN', 'UAH', 'LRD', 'DOP',
    'BRL', 'LAK', 'TJS', 'TTD', 'AED', 'XPT', 'GTQ', 'BTC',
    'INR', 'DJF', 'GMD', 'LBP', 'BTN', 'CNY', 'VEF', 'MWK',
    'MVR', 'KYD', 'SEK', 'CHF', 'LSL', 'NZD', 'MZN', 'HKD',
    'KZT', 'GNF', 'BBD', 'NOK', 'TRY', 'DKK', 'SRD', 'SLL',
    'XAF', 'SHP', 'GIP', 'HUF', 'LTC', 'BYN', 'ETH', 'DGB',
    'DATA', 'BURST',
]

BOT_PARSERS = [
    'app.parsers.simple_parser.SimpleParser',
]

LANGUAGES = (
    'en_US',
)

LANGUAGE_CODE = 'en_US'

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}
