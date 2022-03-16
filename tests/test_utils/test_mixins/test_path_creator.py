import unittest
from pathlib import Path
from unittest import mock

from clovars.utils import PathCreatorMixin
from tests import SKIP_TESTS


class TestPathCreatorMixin(unittest.TestCase):
    """Class representing unit-tests for clovars.utils.mixins.path_creator.PathCreatorMixin class."""
    test_folder = "TEST_FOLDER"

    def setUp(self) -> None:
        """Sets up the test case subject (a PathCreatorMixin instance)."""
        self.path_creator = PathCreatorMixin(folder=self.test_folder)

    def tearDown(self) -> None:
        """Tears down the test case by removing the test folder (if it was created)."""
        if (path := Path(self.test_folder)).exists():
            path.rmdir()

    def test_path_creator_has_path_attribute(self) -> None:
        """Tests whether the PathCreator has the "path" attribute (a Path instance)."""
        self.assertTrue(hasattr(self.path_creator, 'path'))
        self.assertIsInstance(self.path_creator.path, Path)

    def test_create_path_calls_path_mkdir_method(self) -> None:
        """Tests whether the "create_path" method calls the Path's "mkdir" method."""
        with mock.patch('clovars.utils.mixins.path_creator.Path.mkdir') as mock_mkdir:
            self.path_creator.create_path(folder=self.test_folder)
        mock_mkdir.assert_called_once_with(exist_ok=True)

    def test_create_path_returns_a_path_object(self) -> None:
        """Tests whether the "create_path" method returns a Path object."""
        return_value = self.path_creator.create_path(folder=self.test_folder)
        self.assertIsInstance(return_value, Path)

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_delete_if_empty_method(self) -> None:
        """docstring."""
        self.fail('Write the test!')
