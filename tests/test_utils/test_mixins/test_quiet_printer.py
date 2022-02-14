import unittest
from unittest import mock

from clovars.utils import QuietPrinterMixin


class TestQuietPrinterMixin(unittest.TestCase):
    """Class representing unit-tests for clovars.utils.mixins.quiet_printer.QuietPrinterMixin class."""
    def setUp(self) -> None:
        """Sets up the test case subject (a QuietPrinterMixin instance)."""
        self.quiet_printer = QuietPrinterMixin()

    def test_quiet_printer_has_verbose_attribute(self) -> None:
        """Tests whether the QuietPrinter has the "verbose" attribute (a boolean flag)."""
        self.assertTrue(hasattr(self.quiet_printer, 'verbose'))
        self.assertIsInstance(self.quiet_printer.verbose, bool)

    def test_quiet_print_method_calls_print_when_verbose_flag_is_true(self) -> None:
        """Tests whether the "quiet_print" method calls the "print" function when the verbose flag is True."""
        self.quiet_printer.verbose = True
        with mock.patch('builtins.print') as mock_print:
            self.quiet_printer.quiet_print('message')
        mock_print.assert_called_once_with('message')

    def test_quiet_print_method_does_not_call_print_when_verbose_flag_is_false(self) -> None:
        """Tests whether the "quiet_print" method does not call the "print" function when the verbose flag is False."""
        self.quiet_printer.verbose = False
        with mock.patch('builtins.print') as mock_print:
            self.quiet_printer.quiet_print('message')
        mock_print.assert_not_called()
