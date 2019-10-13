from app.tasks import PairData
from suite.test.testcases import SimpleTestCase


class TasksTest(SimpleTestCase):
    def test_todo(self):
        self.assertTrue(PairData)
