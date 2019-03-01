from suite.test.testcases import SimpleTestCase
from suite.test.utils import override_settings
from suite.conf import settings


@override_settings(VAR_OVERRIDE=5555)
class ConfTestTest(SimpleTestCase):
    def test_settings(self):
        self.assertEqual(settings.VAR_OVERRIDE, 5555)

    @override_settings(VAR_OVERRIDE=1111)
    def test_override_settings(self):
        self.assertEqual(settings.VAR_OVERRIDE, 1111)
