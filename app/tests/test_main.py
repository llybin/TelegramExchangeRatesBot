from telegram import Update

from app.main import error_callback
from suite.test.testcases import SimpleTestCase


class MainTest(SimpleTestCase):
    def test_error_handler(self):
        class CallbackContext(object):
            error = "error msg"

        self.assertIsNone(error_callback(Update("0"), CallbackContext()))
