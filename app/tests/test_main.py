from suite.test.testcases import SimpleTestCase

from app.main import error_callback


class MainTest(SimpleTestCase):
    def test_error_handler(self):
        self.assertIsNone(error_callback(None, None))
