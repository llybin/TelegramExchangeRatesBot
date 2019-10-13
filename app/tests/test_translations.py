from app.translations import get_translations, init_translations, transform_locale
from suite.test.testcases import SimpleTestCase


class TranslationsTest(SimpleTestCase):
    def setUp(self) -> None:
        init_translations()

    def test_1_exists(self):
        self.assertTrue(get_translations("en"))

    def test_1_not_exists(self):
        self.assertTrue(get_translations("qq"))

    def test_2_exists(self):
        self.assertTrue(get_translations("en-us"))

    def test_2_not_exists(self):
        self.assertTrue(get_translations("qq-qq"))

    def test_2_4_exists(self):
        self.assertTrue(get_translations("zh-hans"))

    def test_2_4_not_exists(self):
        self.assertTrue(get_translations("qq-qqqq"))

    def test_3_exists(self):
        self.assertTrue(get_translations("zh-hans-sg"))

    def test_3_not_exists(self):
        self.assertTrue(get_translations("qq-qqqq-qq"))


class TransformLocaleTest(SimpleTestCase):
    def setUp(self) -> None:
        init_translations()

    def test_1(self):
        self.assertEqual(transform_locale("ru"), "ru")

    def test_2(self):
        self.assertEqual(transform_locale("en-us"), "en_US")

    def test_2_4(self):
        self.assertEqual(transform_locale("zh-hans"), "zh_Hans")

    def test_3(self):
        self.assertEqual(transform_locale("zh-hans-sg"), "zh_Hans_SG")

    def test_unknown(self):
        self.assertEqual(transform_locale("zh-hans-sg-any"), "en")
        self.assertEqual(transform_locale("zh-h"), "en")
