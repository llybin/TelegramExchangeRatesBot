from suite.test.testcases import SimpleTestCase
from suite.conf import settings


class TestDBTest(SimpleTestCase):
    def test_db_test(self):
        db_name = settings.DATABASE['url'].rsplit('/', 1)[1]
        self.assertTrue(db_name.startswith('test_'))
