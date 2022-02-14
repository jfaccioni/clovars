import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.abstract import Circle
from clovars.bio import Cell, Treatment
from clovars.scientific import ConstantCellSignal, CellSignal, GaussianCellSignal, Gaussian
from clovars.utils import SimulationError
from tests import NotEmptyTestCase


class TestCell(NotEmptyTestCase):
    """Class representing unit-tests for clovars.bio.cell.Cell class."""
    default_delta = 100
    control_treatment = Treatment(
        name="Control",
        division_curve=Gaussian(loc=24.0, scale=5),
        death_curve=Gaussian(loc=32, scale=5),
    )

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the entire test suite by setting the default Treatment."""
        pass

    def setUp(self) -> None:
        """Sets up the test case subject (a Cell instance)."""
        self.cell = Cell()

    def test_cell_has_default_treatment_class_attribute(self) -> None:
        """Tests whether a Cell has a "default_treatment" class attribute (a Treatment instance)."""
        self.assertTrue(hasattr(self.cell, 'default_treatment'))
        self.assertTrue(hasattr(Cell, 'default_treatment'))
        self.assertIsInstance(self.cell.default_treatment, Treatment)

    def test_cell_has_name_attribute(self) -> None:
        """Tests whether a Cell has a "name" attribute (a string)."""
        self.assertTrue(hasattr(self.cell, 'name'))
        self.assertIsInstance(self.cell.name, str)

    def test_cell_has_max_speed_attribute(self) -> None:
        """Tests whether a Cell has a "max_speed" attribute (a float value)."""
        self.assertTrue(hasattr(self.cell, 'max_speed'))
        self.assertIsInstance(self.cell.max_speed, float)

    def test_cell_has_fate_attribute(self) -> None:
        """Tests whether a Cell has a "fate" attribute (a string)."""
        self.assertTrue(hasattr(self.cell, 'fate'))
        self.assertIsInstance(self.cell.fate, str)

    def test_fate_attribute_starts_as_migration(self) -> None:
        """Tests whether a Cell starts with its "fate" attribute set to "migration"."""
        self.assertEqual(Cell().fate, "migration")

    def test_cell_has_seconds_since_birth_attribute(self) -> None:
        """Tests whether a Cell has a "seconds_since_birth" attribute (an integer)."""
        self.assertTrue(hasattr(self.cell, 'seconds_since_birth'))
        self.assertIsInstance(self.cell.seconds_since_birth, int)

    def test_seconds_since_birth_attribute_starts_at_zero(self) -> None:
        """Tests whether a Cell starts with its "seconds_since_birth" attribute set to 0."""
        self.assertEqual(Cell().seconds_since_birth, 0)

    def test_cell_has_alive_attribute(self) -> None:
        """Tests whether a Cell has an "alive" attribute (a boolean value)."""
        self.assertTrue(hasattr(self.cell, 'alive'))
        self.assertIsInstance(self.cell.alive, bool)

    def test_alive_attribute_starts_true(self) -> None:
        """Tests whether a Cell starts with its "alive" attribute set to True."""
        self.assertEqual(Cell().alive, True)

    def test_cell_has_senescent_attribute(self) -> None:
        """Tests whether a Cell has a "senescent" attribute (a boolean value)."""
        self.assertTrue(hasattr(self.cell, 'senescent'))
        self.assertIsInstance(self.cell.senescent, bool)

    def test_senescent_attribute_starts_false(self) -> None:
        """Tests whether a Cell starts with its "senescent" attribute set to False."""
        self.assertEqual(Cell().senescent, False)

    def test_cell_has_fitness_memory_attribute(self) -> None:
        """Tests whether a Cell has a "fitness_memory" attribute (a float)."""
        self.assertTrue(hasattr(self.cell, 'fitness_memory'))
        self.assertIsInstance(self.cell.fitness_memory, float)

    def test_fitness_memory_outside_zero_one_range_raises_error(self) -> None:
        """
        Tests whether a Cell raises a SimulationError only when its "fitness_memory"
        attribute is initialized outside the [0, 1] interval.
        """
        for fitness_memory in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            try:
                Cell(fitness_memory=fitness_memory)
            except SimulationError:
                self.fail(
                    "SimulationError was unexpectedly raised when initializing Cell"
                    f" with fitness_memory = {fitness_memory}"
                )
        for fitness_memory in [-0.1, 1.1]:
            with self.assertRaises(SimulationError):
                Cell(fitness_memory=fitness_memory)

    def test_cell_has_division_threshold_attribute(self) -> None:
        """Tests whether a Cell has a "division_threshold" attribute (a float)."""
        self.assertTrue(hasattr(self.cell, 'division_threshold'))
        self.assertIsInstance(self.cell.division_threshold, float)

    def test_division_threshold_outside_zero_one_range_raises_error(self) -> None:
        """
        Tests whether a Cell raises a SimulationError only when its "division_threshold"
        attribute is initialized outside the [0, 1] interval.
        """
        for division_threshold in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            try:
                Cell(division_threshold=division_threshold)
            except SimulationError:
                self.fail(
                    "SimulationError was unexpectedly raised when initializing Cell"
                    f" with division_threshold = {division_threshold}"
                )
        for division_threshold in [-0.1, 1.1]:
            with self.assertRaises(SimulationError):
                Cell(division_threshold=division_threshold)

    def test_cell_division_threshold_attribute_is_between_zero_and_one(self) -> None:
        """
        Tests whether the "division_threshold" attribute (random float value) lies between 0 and 1
        when it is initialized as a None value.
        """
        for _ in range(10):
            cell = Cell(division_threshold=None)
            with self.subTest(cell=cell):
                self.assertGreaterEqual(cell.division_threshold, 0)
                self.assertLessEqual(cell.division_threshold, 1)

    def test_cell_has_death_threshold_attribute(self) -> None:
        """Tests whether a Cell has a "death_threshold" attribute (a float)."""
        self.assertTrue(hasattr(self.cell, 'death_threshold'))
        self.assertIsInstance(self.cell.death_threshold, float)

    def test_death_threshold_outside_zero_one_range_raises_error(self) -> None:
        """
        Tests whether a Cell raises a SimulationError only when its "death_threshold"
        attribute is initialized outside the [0, 1] interval.
        """
        for death_threshold in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            try:
                Cell(death_threshold=death_threshold)
            except SimulationError:
                self.fail(
                    "SimulationError was unexpectedly raised when initializing Cell"
                    f" with death_threshold = {death_threshold}"
                )
        for death_threshold in [-0.1, 1.1]:
            with self.assertRaises(SimulationError):
                Cell(death_threshold=death_threshold)

    def test_cell_death_threshold_attribute_is_between_zero_and_one(self) -> None:
        """
        Tests whether the "death_threshold" attribute (random float value) lies between 0 and 1
        when it is initialized as a None value.
        """
        for _ in range(10):
            cell = Cell(death_threshold=None)
            with self.subTest(cell=cell):
                self.assertGreaterEqual(cell.death_threshold, 0)
                self.assertLessEqual(cell.death_threshold, 1)

    def test_cell_has_death_threshold_attribute_is_between_zero_and_one(self) -> None:
        """Tests whether the "death_threshold" attribute (random float value) lies between 0 and 1."""
        for _ in range(10):
            cell = Cell()
            with self.subTest(cell=cell):
                self.assertGreaterEqual(cell.death_threshold, 0)
                self.assertLessEqual(cell.death_threshold, 1)

    def test_cell_has_circle_attribute(self) -> None:
        """Tests whether a Cell has a "circle" attribute (a Circle instance)."""
        self.assertTrue(hasattr(self.cell, 'circle'))
        self.assertIsInstance(self.cell.circle, Circle)

    def test_cell_has_signal_attribute(self) -> None:
        """Tests whether a Cell has a "signal" attribute (a CellSignal instance)."""
        self.assertTrue(hasattr(self.cell, 'signal'))
        self.assertIsInstance(self.cell.signal, CellSignal)

    def test_cell_uses_a_constant_signal_if_signal_argument_is_none(self) -> None:
        """Tests whether a Cell uses a ConstantCellSignal instance when initialized with signal=None."""
        cell = Cell(signal=None)
        self.assertIsInstance(cell.signal, ConstantCellSignal)

    def test_cell_has_treatment_attribute(self) -> None:
        """Tests whether a Cell has a "treatment" attribute (a Treatment instance)."""
        self.assertTrue(hasattr(self.cell, 'treatment'))
        self.assertIsInstance(self.cell.treatment, Treatment)

    def test_cell_uses_the_default_treatment_if_treatment_argument_is_none(self) -> None:
        """Tests whether a Cell uses the "default_treatment" class attribute when initialized with treatment=None."""
        cell = Cell(signal=None)
        self.assertIs(cell.treatment, self.cell.default_treatment)

    def test_calculate_division_chance_method_returns_chance_depending_on_the_cell_seconds_since_birth(self) -> None:
        """
        Tests whether the "calculate_division_chance" method returns a chance between
        [0, 1] proportional to the Cell's age.
        """
        self.cell.treatment = self.control_treatment  # division stats: 24 (+-5) hours
        self.cell.seconds_since_birth = 0  # Very low chance of dividing right after birth
        self.assertLess(self.cell.calculate_division_chance(delta=self.default_delta), 0.1)
        self.cell.seconds_since_birth = 60 * 60 * 1000  # Very high chance of dividing after 1000 h
        self.assertGreater(self.cell.calculate_division_chance(delta=self.default_delta), 0.9)

    def test_calculate_death_chance_method_returns_chance_depending_on_the_cell_seconds_since_birth(self) -> None:
        """
        Tests whether the "calculate_death_chance" method returns a chance between
        [0, 1] proportional to the Cell's age.
        """
        self.cell.treatment = self.control_treatment  # death stats: 24 (+-5) hours
        self.cell.seconds_since_birth = 0  # Very low chance of dying right after birth
        self.assertLess(self.cell.calculate_death_chance(delta=self.default_delta), 0.1)
        self.cell.seconds_since_birth = 60 * 60 * 1000  # Very high chance of dying after 1000 h
        self.assertGreater(self.cell.calculate_death_chance(delta=self.default_delta), 0.9)

    def test_cell_has_circle_attributes_as_properties(self) -> None:
        """Tests whether a Cell exposes relevant Circle attributes as properties."""
        test_cell = Cell(x=10.0, y=20.0, radius=5.0)
        for attr_name in ['x', 'y', 'radius', 'center', 'area']:
            with self.subTest(attr_name=attr_name):
                try:
                    value = getattr(test_cell, attr_name)
                    self.assertEqual(value, getattr(test_cell.circle, attr_name))
                except AttributeError:
                    self.fail(f"Test failed: could not get attribute {attr_name} in Cell instance {test_cell}")

    def test_cell_is_able_to_set_circle_attributes(self) -> None:
        """Tests whether a Cell is able to directly set its "x", "y" and "radius" Circle attributes."""
        test_cell = Cell(x=10.0, y=20.0, radius=5.0)
        for attr_name in ['x', 'y', 'radius']:
            with self.subTest(attr_name=attr_name):
                try:
                    setattr(test_cell, attr_name, 1.0)
                except AttributeError:
                    self.fail(f"Test failed: could not set attribute {attr_name} in Cell instance {test_cell}")

    def test_cell_distance_to_method_calculates_cell_distance_using_circles(self) -> None:
        """Tests whether the "distance_to" method uses Circles to calculate distance between Cells."""
        other_cell = Cell()
        with mock.patch("clovars.abstract.Circle.distance_to") as mock_circle_distance_to:
            self.cell.distance_to(other_cell=other_cell)
        mock_circle_distance_to.assert_called_once_with(other_cell.circle)

    def test_cell_distance_to_method_raises_type_error_if_argument_is_not_a_cell(self) -> None:
        """
        Tests whether the "distance_to" method raises a TypeError only when the
        other_cell argument is not an actual Cell instance.
        """
        valid_argument = Cell()
        try:
            self.cell.distance_to(other_cell=valid_argument)
        except TypeError:
            self.fail("Cell raised TypeError unexpectedly!")
        invalid_argument = "WHATEVER ELSE"
        with self.assertRaises(TypeError):
            self.cell.distance_to(other_cell=invalid_argument)  # noqa

    def test_cell_has_hours_since_birth_property(self) -> None:
        """Tests whether a Cell has an "hours_since_birth" property (a float)."""
        self.assertTrue(hasattr(self.cell, 'hours_since_birth'))
        self.assertIsInstance(self.cell.hours_since_birth, float)

    def test_hours_since_birth_calculations_are_correct(self) -> None:
        """Tests whether the "hours_since_birth" property correctly calculates the Cell's hours since birth."""
        for seconds, hours in [(0, 0.0), (60, 1/60), (3600, 1.0), (7200, 2.0), (9000, 2.5)]:
            with self.subTest(seconds=seconds, hours=hours):
                self.cell.seconds_since_birth = seconds
                self.assertEqual(self.cell.hours_since_birth, hours)

    def test_cell_has_branch_name_property(self) -> None:
        """Tests whether a Cell has a "branch_name" property (a string)."""
        self.assertTrue(hasattr(self.cell, 'branch_name'))
        self.assertIsInstance(self.cell.branch_name, str)

    def test_branch_name_returns_root_name_up_to_first_division(self) -> None:
        """Tests whether the "branch_name" property returns the Cell's root name, including the branch number."""
        for cell_name, branch_name in [('1', '1'), ('3b.1', '3b'), ('15e-5.1.2', '15e-5'), ('4d-3.2.2.1.2', '4d-3')]:
            with self.subTest(cell_name=cell_name, branch_name=branch_name):
                self.cell.name = cell_name
                self.assertEqual(self.cell.branch_name, branch_name)

    def test_cell_has_colony_name_property(self) -> None:
        """Tests whether a Cell has a "colony_name" property (a string)."""
        self.assertTrue(hasattr(self.cell, 'colony_name'))
        self.assertIsInstance(self.cell.colony_name, str)

    def test_colony_name_returns_root_name_up_to_branch_name(self) -> None:
        """Tests whether the "colony_name" property returns the Cell's root name, excluding the branch number."""
        for cell_name, colony_name in [('1', '1'), ('3b.1', '3b'), ('15e-5.1.2', '15e'), ('4d-3.2.2.1.2', '4d')]:
            with self.subTest(cell_name=cell_name, colony_name=colony_name):
                self.cell.name = cell_name
                self.assertEqual(self.cell.colony_name, colony_name)

    def test_cell_has_generation_property(self) -> None:
        """Tests whether a Cell has a "generation" property (an integer)."""
        self.assertTrue(hasattr(self.cell, 'generation'))
        self.assertIsInstance(self.cell.generation, int)

    def test_generation_returns_cell_name_prefix(self) -> None:
        """
        Tests whether the "generation" property returns the number of times that the Cell has divided
        based on its name.
        """
        for cell_name, generation in [('1', 0), ('3b.1', 1), ('15e-5.1.2', 2), ('4d-3.2.2.1.2', 4)]:
            with self.subTest(cell_name=cell_name, generation=generation):
                self.cell.name = cell_name
                self.assertEqual(self.cell.generation, generation)

    def test_cell_has_signal_value_property(self) -> None:
        """Tests whether a Cell has a "signal_value" property (a float)."""
        self.assertTrue(hasattr(self.cell, 'signal_value'))
        self.assertIsInstance(self.cell.signal_value, float)

    def test_signal_value_returns_current_signal_value(self) -> None:
        """Tests whether the "signal_value" property returns the CellSignal's current value."""
        signal = GaussianCellSignal()
        test_cell = Cell(signal=signal)
        for _ in range(10):
            signal.oscillate(current_seconds=0)
            current_signal_value = signal.value
            with self.subTest(current_signal_value=current_signal_value):
                self.assertEqual(test_cell.signal_value, current_signal_value)

    def test_set_cell_fate_method_sets_fate_to_death_if_cell_should_die(self) -> None:
        """
        Tests whether the "set_cell_fate" method sets the Cell fate to "death"
        if the "should_die" method returns True.
        """
        with mock.patch('clovars.bio.Cell.should_die', return_value=True):
            self.cell.set_cell_fate(delta=self.default_delta)
        self.assertEqual(self.cell.fate, "death")

    def test_should_die_returns_boolean_based_on_death_chance_and_threshold(self) -> None:
        """Tests whether the "should_die" method returns True/False depending on the Cell's death chance."""
        self.cell.death_threshold = 1.1  # death chance is in [0, 1], cell never dies here
        self.assertFalse(self.cell.should_die(delta=self.default_delta))
        self.cell.death_threshold = -0.1  # death chance is in [0, 1], cell always dies here
        self.assertTrue(self.cell.should_die(delta=self.default_delta))

    def test_set_cell_fate_method_sets_fate_to_division_if_cell_should_divide(self) -> None:
        """
        Tests whether the "set_cell_fate" method sets the Cell fate to "division"
        if the "should_die" method returns False and "should_divide" returns True.
        """
        with (
                mock.patch('clovars.bio.Cell.should_die', return_value=False),
                mock.patch('clovars.bio.Cell.should_divide', return_value=True),
        ):
            self.cell.set_cell_fate(delta=self.default_delta)
        self.assertEqual(self.cell.fate, "division")

    def test_should_divide_returns_boolean_based_on_division_chance_and_threshold(self) -> None:
        """Tests whether the "should_divide" method returns True/False depending on the Cell's division chance."""
        self.cell.division_threshold = 1.1  # death chance is in [0, 1], cell never dies here
        self.assertFalse(self.cell.should_divide(delta=self.default_delta))
        self.cell.division_threshold = -0.1  # death chance is in [0, 1], cell always dies here
        self.assertTrue(self.cell.should_divide(delta=self.default_delta))

    def test_set_cell_fate_method_sets_fate_to_migration_if_cell_should_not_die_nor_divide(self) -> None:
        """
        Tests whether the "set_cell_fate" method sets the Cell fate to "migration"
        if both "should_die" and "should_divide" methods returns False.
        """
        with (
                mock.patch('clovars.bio.Cell.should_die', return_value=False),
                mock.patch('clovars.bio.Cell.should_divide', return_value=False),
        ):
            self.cell.set_cell_fate(delta=self.default_delta)
        self.assertEqual(self.cell.fate, "migration")

    @mock.patch('clovars.bio.Cell.migrate')
    @mock.patch('clovars.bio.Cell.divide')
    @mock.patch('clovars.bio.Cell.die')
    def test_pass_time_method_calls_die_if_cell_fate_is_to_die(
            self,
            mock_die: MagicMock,
            mock_divide: MagicMock,
            mock_migrate: MagicMock,
    ) -> None:
        """Tests whether the "pass_time" method calls the "die" method if the Cell fate is set to "death"."""
        self.cell.fate = 'death'
        self.cell.pass_time(delta=self.default_delta, current_seconds=0)
        mock_die.assert_called_once()
        mock_divide.assert_not_called()
        mock_migrate.assert_not_called()

    def test_pass_time_method_returns_none_if_cell_fate_is_to_die(self) -> None:
        """Tests whether the "pass_time" method returns None if the Cell fate is set to "death"."""
        self.cell.fate = 'death'
        return_value = self.cell.pass_time(delta=self.default_delta, current_seconds=0)
        self.assertIsNone(return_value)

    @mock.patch('clovars.bio.Cell.migrate')
    @mock.patch('clovars.bio.Cell.divide')
    @mock.patch('clovars.bio.Cell.die')
    def test_pass_time_method_calls_divide_if_cell_fate_is_to_divide(
            self,
            mock_die: MagicMock,
            mock_divide: MagicMock,
            mock_migrate: MagicMock,
    ) -> None:
        """Tests whether the "pass_time" method calls the "divide" method if the Cell fate is set to "division"."""
        self.cell.fate = 'division'
        self.cell.pass_time(delta=self.default_delta, current_seconds=0)
        mock_die.assert_not_called()
        mock_divide.assert_called_once()
        mock_migrate.assert_not_called()

    def test_pass_time_method_returns_a_tuple_of_child_cells_if_cell_fate_is_to_divide(self) -> None:
        """Tests whether the "pass_time" method returns a tuple of child Cells if the Cell fate is set to "division"."""
        self.cell.fate = 'division'
        return_value = self.cell.pass_time(delta=self.default_delta, current_seconds=0)
        self.assertIsInstance(return_value, tuple)
        for thing in return_value:
            self.assertIsInstance(thing, Cell)
            self.assertIsNot(thing, self.cell)

    @mock.patch('clovars.bio.Cell.migrate')
    @mock.patch('clovars.bio.Cell.divide')
    @mock.patch('clovars.bio.Cell.die')
    def test_pass_time_method_calls_migrate_if_cell_fate_is_to_migrate(
            self,
            mock_die: MagicMock,
            mock_divide: MagicMock,
            mock_migrate: MagicMock,
    ) -> None:
        """Tests whether the "pass_time" method calls the "migrate" method if the Cell fate is set to "migration"."""
        self.cell.fate = 'migration'
        self.cell.pass_time(delta=self.default_delta, current_seconds=0)
        mock_die.assert_not_called()
        mock_divide.assert_not_called()
        mock_migrate.assert_called_once()

    def test_pass_time_method_returns_the_same_cell_if_cell_fate_is_to_migrate(self) -> None:
        """Tests whether the "pass_time" method returns the own Cell instance if the Cell fate is set to "migration"."""
        self.cell.fate = 'migration'
        return_value = self.cell.pass_time(delta=self.default_delta, current_seconds=0)
        self.assertIsInstance(return_value, Cell)
        self.assertIs(return_value, self.cell)

    def test_pass_time_method_raises_value_error_if_cell_fate_is_unexpected(self) -> None:
        """Tests whether the "pass_time" method raises a ValueError if the Cell fate value is unexpected."""
        self.cell.fate = 'UNEXPECTED VALUE!'
        with self.assertRaises(ValueError):
            self.cell.pass_time(delta=self.default_delta, current_seconds=0)

    def test_die_method_sets_the_state_of_the_alive_flag_to_false(self) -> None:
        """Tests whether the "die" method sets the state of the "alive" flag to False."""
        self.assertTrue(self.cell.alive)
        self.cell.die()
        self.assertFalse(self.cell.alive)

    def test_divide_method_returns_a_tuple_of_two_cells_with_matching_names(self) -> None:
        """Tests whether the "divide" returns a tuple of two child Cells with matching names (ending in .1 and .2)."""
        children = self.cell.divide(delta=self.default_delta)
        self.assertIsInstance(children[0], Cell)
        self.assertEqual(children[0].name, self.cell.name + '.1')
        self.assertIsInstance(children[1], Cell)
        self.assertEqual(children[1].name, self.cell.name + '.2')

    def test_get_child_cell_returns_a_new_cell_instance(self) -> None:
        """Tests whether the "get_child_cell" method returns a new Cell instance."""
        child_cell = self.cell.get_child_cell(delta=self.default_delta, branch_name='')
        self.assertIsInstance(child_cell, Cell)
        self.assertIsNot(child_cell, self.cell)

    def test_get_child_cell_adds_the_branch_name_to_the_parent_cell_name(self) -> None:
        """Tests whether the Cell returned from "get_child_cell" has the same base name as its parent + branch name."""
        for branch_name in ['1', '2', 'BRANCH_NAME', '...', '']:
            child_cell = self.cell.get_child_cell(delta=self.default_delta, branch_name=branch_name)
            with self.subTest(branch_name=branch_name):
                self.assertEqual(child_cell.name, f"{self.cell.name}.{branch_name}")

    def test_get_child_cell_method_moves_cell(self) -> None:
        """Tests whether the "migrate" method moves the Cell from its previous position."""
        previous_cell_center = self.cell.center
        same_cell = self.cell.migrate(delta=self.default_delta)
        self.assertNotEqual(same_cell.center, previous_cell_center)  # unlikely to be equal, but it may happen...

    def test_get_child_cell_copies_attributes_from_parent_cell(self) -> None:
        """Tests whether the Cell returned from "get_child_cell" has some identical attributes as its parent."""
        child_cell = self.cell.get_child_cell(delta=self.default_delta, branch_name='')
        for attr_name in ['max_speed', 'radius', 'fitness_memory', 'treatment']:
            with self.subTest(attr_name=attr_name):
                self.assertEqual(getattr(child_cell, attr_name), getattr(self.cell, attr_name))

    def test_get_child_cell_calls_get_child_fitness_to_assign_a_the_child_thresholds(self) -> None:
        """
        Tests whether the Cell returned from "get_child_cell" has a division and death threshold values
        returned from the parent's "get_child_fitness" method.
        """
        mock_fitness = (0.1, 0.2)
        with mock.patch.object(self.cell, 'get_child_fitness', return_value=mock_fitness) as mock_get_cell_fitness:
            child_cell = self.cell.get_child_cell(delta=self.default_delta, branch_name='')
        mock_get_cell_fitness.assert_called()
        self.assertIn(child_cell.division_threshold, mock_fitness)
        self.assertIn(child_cell.death_threshold, mock_fitness)

    def test_get_child_cell_uses_signal_split_to_assign_a_new_signal_to_child_cell(self) -> None:
        """
        Tests whether the Cell returned from "get_child_cell" has a signal
        returned from the parent's signal's "split" method.
        """
        with mock.patch('clovars.scientific.CellSignal.split') as mock_split:
            child_cell = self.cell.get_child_cell(delta=self.default_delta, branch_name='')
        mock_split.assert_called_once()
        self.assertIs(child_cell.signal, mock_split.return_value)

    def test_get_new_xy_coordinates_method_returns_a_tuple_of_floats(self) -> None:
        """Tests whether the "get_new_xy_coordinates" method returns a tuple of floats."""
        xy = self.cell.get_new_xy_coordinates(delta=self.default_delta, event_name='migration')
        self.assertIsInstance(xy, tuple)
        for thing in xy:
            self.assertIsInstance(thing, float)

    def test_get_new_xy_coordinates_method_raises_value_error_if_event_name_is_not_migration_or_division(self) -> None:
        """
        Tests whether the "get_new_xy_coordinates" raises a ValueError if the
        event name argument isn't "migration" or "division".
        """
        for event_name in ['migration', 'division']:
            with self.subTest(event_name=event_name):
                try:
                    self.cell.get_new_xy_coordinates(delta=self.default_delta, event_name='migration')
                except ValueError:
                    self.fail(f'Call to "get_new_xy_coordinates" failed unexpectedly with event_name="{event_name}"')
        with self.assertRaises(ValueError):
            self.cell.get_new_xy_coordinates(delta=self.default_delta, event_name="INVALID EVENT NAME")

    def test_get_new_xy_coordinates_method_uses_smaller_search_radius_on_division(self) -> None:
        """Tests whether the "get_new_xy_coordinates" uses a smaller search radius when the event name is "division"."""
        with mock.patch('clovars.bio.cell.Circle') as mock_circle_init_migration:
            self.cell.get_new_xy_coordinates(delta=self.default_delta, event_name='migration')
        migration_radius = mock_circle_init_migration.call_args[1]['radius']
        with mock.patch('clovars.bio.cell.Circle') as mock_circle_init_division:
            self.cell.get_new_xy_coordinates(delta=self.default_delta, event_name='division')
        division_radius = mock_circle_init_division.call_args[1]['radius']
        self.assertGreater(migration_radius, division_radius)

    def test_get_child_fitness_method_returns_tuple_of_floats(self) -> None:
        """
        Tests whether the "get_child_fitness" method returns a tuple of floats
        representing the child Cell's division and death thresholds.
        """
        return_value = self.cell.get_child_fitness()
        self.assertIsInstance(return_value, tuple)
        with self.assertSequenceNotEmpty(return_value):
            for thing in return_value:
                self.assertIsInstance(thing, float)

    def test_get_child_fitness_method_returns_values_from_bounded_brownian_fluctuation_function(self) -> None:
        """
        Tests whether the "get_child_fitness" method returns values from the
        "bounded_brownian_fluctuation_function" function using the appropriate parameters from the Cell.
        """
        with mock.patch('clovars.bio.cell.bounded_brownian_motion') as mock_brownian_motion:
            self.cell.get_child_fitness()
        mock_brownian_motion.assert_any_call(current_value=self.cell.division_threshold, scale=self.cell.fitness_memory)
        mock_brownian_motion.assert_any_call(current_value=self.cell.death_threshold, scale=self.cell.fitness_memory)

    def test_migrate_method_returns_the_same_cell(self) -> None:
        """Tests whether the "migrate" method returns the same Cell."""
        same_cell = self.cell.migrate(delta=self.default_delta)
        self.assertIs(same_cell, self.cell)

    def test_migrate_method_adds_delta_seconds_to_the_cell_seconds_since_birth(self) -> None:
        """Tests whether the "migrate" method adds delta seconds to the Cell's "seconds_since_birth" attribute."""
        previous_seconds_since_birth = self.cell.seconds_since_birth
        same_cell = self.cell.migrate(delta=self.default_delta)
        self.assertEqual(same_cell.seconds_since_birth, previous_seconds_since_birth + self.default_delta)

    def test_migrate_method_moves_cell(self) -> None:
        """Tests whether the "migrate" method moves the Cell from its previous position."""
        previous_cell_center = self.cell.center
        same_cell = self.cell.migrate(delta=self.default_delta)
        self.assertNotEqual(same_cell.center, previous_cell_center)  # unlikely to be equal, but it may happen...

    def test_fluctuate_signal_method_calls_signal_oscillate_method(self) -> None:
        """Tests whether the "fluctuate_signal" method calls the signal's "oscillate" method."""
        self.cell.signal = (signal_mock := MagicMock())
        self.cell.fluctuate_signal(current_seconds=0)
        signal_mock.oscillate.assert_called_once_with(current_seconds=0)


if __name__ == '__main__':
    unittest.main()
