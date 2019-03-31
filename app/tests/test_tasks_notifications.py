from suite.test.testcases import SimpleTestCase

from app.tasks_notifications import PriceRequest


class TasksTest(SimpleTestCase):
    def test_todo(self):
        self.assertTrue(PriceRequest)
