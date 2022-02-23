import unittest

from clovars._deprecated.settings import get_run_settings, get_view_settings, get_analysis_settings


@unittest.skip("Deprecated module")
class TestSettings(unittest.TestCase):
    """Class representing unit-tests of the clovars.settings module."""
    def test_get_settings_functions_returns_dictionaries(self) -> None:
        """Tests whether the "get...settings" functions returns dictionaries with string as keys."""
        for func in [get_run_settings, get_view_settings, get_analysis_settings]:
            with self.subTest(func=func):
                return_value = get_run_settings()
                self.assertIsInstance(return_value, dict)
                for key in return_value:
                    self.assertIsInstance(key, str)


if __name__ == '__main__':
    unittest.main()
