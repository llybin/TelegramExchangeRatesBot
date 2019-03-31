from suite.test.testcases import SimpleTestCase

from app.main import error_handler


class MainTest(SimpleTestCase):
    def test_error_handler(self):
        self.assertIsNone(error_handler(None, None, None))
