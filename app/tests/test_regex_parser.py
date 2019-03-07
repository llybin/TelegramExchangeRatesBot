# TODO:
# migrations/versions/79fd60fe1187_currencies_chat_request_foreigns.py
# app/tests/fixtures/currencies.py
#
# import unittest
# from unittest.mock import patch
#
# from app.parsers.base import PriceRequest
# from app.parsers.regex_parser import RegexParser
# from .fixtures.currencies import ALL_CURRENCIES
#
#
# class RegexParserTest(unittest.TestCase):
#     @patch('app.parsers.regex_parser.get_all_currencies', return_value=ALL_CURRENCIES)
#     def test_cross_all_currency(self, m):
#         for cur0 in ALL_CURRENCIES:
#             for cur1 in ALL_CURRENCIES:
#                 # print(f'{cur0} {cur1}')
#                 self.assertEqual(RegexParser(f'{cur0} {cur1}').parse(),
#                                  PriceRequest(amount=None, currency=cur0, to_currency=cur1))  # NOQA
#                 # print(f'{cur1} {cur0}')
#                 self.assertEqual(RegexParser(f'{cur1} {cur0}').parse(),
#                                  PriceRequest(amount=None, currency=cur1, to_currency=cur0))  # NOQA
