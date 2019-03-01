import os
import sys
import unittest


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.tearDown()

    def tearDown(self):
        try:
            del sys.modules['suite']
            del sys.modules['suite.conf']
            del sys.modules['suite.conf.exceptions']
            del sys.modules['suite.conf.global_settings']
            del sys.modules['suite.conf.tests']
            del sys.modules['suite.conf.tests.base_settings']
            del sys.modules['suite.conf.tests.testing_settings']

        except KeyError:
            pass

    def test_config_environment(self):
        from suite.conf.tests.settings.base_settings import NAME
        from suite.conf import settings

        os.environ["SETTINGS_MODULE"] = "suite.conf.tests.settings.base_settings"

        self.assertIsNotNone(settings.NAME)
        self.assertEqual(os.environ.get("SETTINGS_MODULE"), "suite.conf.tests.settings.base_settings")
        self.assertEqual(settings.NAME, NAME)
        self.assertTrue(settings.configured)

    def test_config_new_environment(self):
        from suite.conf.tests.settings.testing_settings import NAME
        from suite.conf import settings

        os.environ["SETTINGS_MODULE"] = "suite.conf.tests.settings.testing_settings"

        self.assertEqual(os.environ.get("SETTINGS_MODULE"), "suite.conf.tests.settings.testing_settings")
        self.assertIsNotNone(settings.NAME)
        self.assertEqual(settings.NAME, NAME)
        self.assertTrue(settings.configured)
