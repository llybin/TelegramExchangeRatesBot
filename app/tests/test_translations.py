from suite.test.testcases import SimpleTestCase

from app.translations import get_translations, init_translations


class TranslationsTest(SimpleTestCase):
    def setUp(self) -> None:
        init_translations()

    def test_1_exists(self):
        self.assertTrue(get_translations('en'))

    def test_1_not_exists(self):
        self.assertTrue(get_translations('qq'))

    def test_2_exists(self):
        self.assertTrue(get_translations('en-us'))

    def test_2_not_exists(self):
        self.assertTrue(get_translations('qq-qq'))

    def test_2_4_exists(self):
        self.assertTrue(get_translations('zh-hans'))

    def test_2_4_not_exists(self):
        self.assertTrue(get_translations('qq-qqqq'))

    def test_3_exists(self):
        self.assertTrue(get_translations('zh-hans-sg'))

    def test_3_not_exists(self):
        self.assertTrue(get_translations('qq-qqqq-qq'))
