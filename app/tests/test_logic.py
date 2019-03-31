from suite.test.testcases import SimpleTestCase
from suite.conf import settings

from app.logic import PARSERS


class ParsingTest(SimpleTestCase):
    def test_parsers(self):
        self.assertEqual(
            list(map(lambda x: x.__name__, PARSERS)),
            list(map(lambda x: x.rsplit('.', 1)[1], settings.BOT_PARSERS))
        )
