from suite.test.testcases import SimpleTestCase

from ..logic import get_all_currencies


class LogicTest(SimpleTestCase):
    def test_example(self):
        self.assertEqual(len(get_all_currencies()), 394)
