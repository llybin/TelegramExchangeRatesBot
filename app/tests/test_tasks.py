from suite.test.testcases import SimpleTestCase

from app.tasks import PairData


class TasksTest(SimpleTestCase):
    def test_todo(self):
        self.assertTrue(PairData)
