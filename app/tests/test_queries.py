from suite.test.testcases import SimpleTestCase

from app.queries import get_all_currencies


class GetAllCurrenciesTest(SimpleTestCase):
    def test_get_all_currencies(self):
        self.assertEqual(len(get_all_currencies()), 210)
