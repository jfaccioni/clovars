from __future__ import annotations

import json
import sys
from typing import Any

import numpy as np
from PySide6 import QtCore as qtc, QtWidgets as qtw
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavBar
from matplotlib.figure import Figure
from scipy.stats.distributions import norm, exponnorm, gamma, lognorm

from clovars.gui import GroupWidget
from clovars.gui.curve import CurveSelectorWidget
from clovars.gui.memory import FitnessMemorySelectorWidget
from clovars.gui.signal import SignalSelectorWidget
from clovars.gui.file_handler import FileHandler


class NewTreatmentController(qtw.QWidget):
    """Widget bundling all widgets related to creating a new Treatment."""
    treatmentNameChanged = qtc.Signal(str)
    divisionCurveChanged = qtc.Signal(dict)
    deathCurveChanged = qtc.Signal(dict)
    saveTreatmentRequested = qtc.Signal(dict)
    loadTreatmentRequested = qtc.Signal()
    cancelTreatmentRequested = qtc.Signal()

    def __init__(
            self,
            parent: qtw.QWidget = None,
    ) -> None:
        """Initializes a NewTreatmentController instance."""
        super().__init__(parent=parent)

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # TREATMENT NAME BOX
        self.line_edit = qtw.QLineEdit()
        self.name_group_widget = GroupWidget(label='Treatment name', widgets=[self.line_edit])
        layout.addWidget(self.name_group_widget)

        # DIVISION CURVES BOX
        self.division_curve_widget = CurveSelectorWidget(curve_name='Division curve', adjust_margins=True)
        self.death_curve_widget = CurveSelectorWidget(curve_name='Death curve', adjust_margins=True)
        self.curve_group_widget = GroupWidget(
            label='Treatment curves',
            widgets=[self.division_curve_widget, self.death_curve_widget],
        )
        layout.addWidget(self.curve_group_widget)

        # FITNESS MEMORY BOX
        self.fitness_memory_widget = FitnessMemorySelectorWidget(adjust_margins=True)
        self.fitness_memory_group = GroupWidget(label='Fitness memory', widgets=[self.fitness_memory_widget])
        layout.addWidget(self.fitness_memory_group)

        # CELL SIGNAL BOX
        self.cell_signal_widget = SignalSelectorWidget(adjust_margins=True)
        self.cell_signal_group = GroupWidget(label='Cell signal', widgets=[self.cell_signal_widget])
        layout.addWidget(self.cell_signal_group)

        # BUTTONS BOX
        self.load_button = qtw.QPushButton('Load and edit an existing Treatment')
        self.save_button = qtw.QPushButton('Save current Treatment to file')
        self.cancel_button = qtw.QPushButton('Cancel')
        self.buttons_group = GroupWidget(
            label='Options',
            widgets=[self.load_button, self.save_button, self.cancel_button],
            orientation='vertical'
        )
        layout.addWidget(self.buttons_group)

        # SETUP
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setup()

    def setup(self) -> None:
        """Sets up the connections on the TreatmentController."""
        self.line_edit.textChanged.connect(self.treatmentNameChanged)  # noqa
        self.division_curve_widget.curveChanged.connect(self.divisionCurveChanged)  # noqa
        self.death_curve_widget.curveChanged.connect(self.deathCurveChanged)  # noqa
        self.save_button.clicked.connect(self.on_save_button_clicked)  # noqa
        self.load_button.clicked.connect(self.loadTreatmentRequested)  # noqa
        self.cancel_button.clicked.connect(self.cancelTreatmentRequested)  # noqa

    def on_save_button_clicked(self) -> None:
        """Emits a signal containing the Treatment's information."""
        self.saveTreatmentRequested.emit(self.get_value())

    def get_value(self) -> dict:
        """Returns the currently selected Treatment."""
        return {
            'name': self.line_edit.text(),
            'fitness_memory_disturbance': self.get_fitness_memory(),
            'signal_disturbance': self.get_cell_signal(),
            'division_curve': self.get_division_curve(),
            'death_curve': self.get_death_curve(),
        }

    def get_fitness_memory(self) -> float:
        """Returns the currently selected fitness memory value."""
        return self.fitness_memory_widget.get_value()

    def get_cell_signal(self) -> dict[str, Any]:
        """Returns the currently selected cell signal parameters."""
        return self.cell_signal_widget.get_value()

    def get_division_curve(self) -> dict[str, Any]:
        """Returns the currently selected division curve parameters."""
        return self.division_curve_widget.get_value()

    def get_death_curve(self) -> dict[str, Any]:
        """Returns the currently selected death curve parameters."""
        return self.death_curve_widget.get_value()

    def load_from_json(self, json_dict: dict) -> None:
        """Sets values on the interface from a properly-formatted JSON dictionary."""
        self.line_edit.setText(json_dict['name'])
        self.fitness_memory_widget.load_from_json(json_dict['fitness_memory_disturbance'])
        self.cell_signal_widget.load_from_json(json_dict['signal_disturbance'])
        self.division_curve_widget.load_from_json(json_dict['division_curve'])
        self.death_curve_widget.load_from_json(json_dict['death_curve'])


class NewTreatmentView(qtw.QWidget):
    """Widget that dynamically displays a new Treatment."""
    def __init__(
            self,
            initial_division_curve: dict[str, Any] = None,
            initial_death_curve: dict[str, Any] = None,
            parent: qtw.QWidget = None,
    ) -> None:
        """Initializes a NewTreatmentView instance."""
        super().__init__(parent=parent)

        # FIGURE AND AXES
        self.figure = Figure(figsize=(8, 4))
        self.ax = self.figure.subplots()

        # DATA
        self.xs = np.linspace(0, 300, 10_000)
        self.division_ys = np.full(self.xs.shape, np.nan)
        if initial_division_curve is not None:
            self.division_ys = self.get_curve_values(params=initial_division_curve)
        self.death_ys = np.full(self.xs.shape, np.nan)
        if initial_death_curve is not None:
            self.death_ys = self.get_curve_values(params=initial_death_curve)

        # LAYOUT
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # CANVAS AND NAVBAR
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.navbar = NavBar(self.canvas, self)
        layout.addWidget(self.navbar)

        self.update_plot()

    def update_plot(self) -> None:
        """Updates the plot."""
        self.ax.clear()
        self.ax.plot(self.xs, self.division_ys, label='Division curve', color='#029e73')
        self.ax.plot(self.xs, self.death_ys, label='Death curve', color='#de8f05')
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Density')
        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def update_plot_title(
            self,
            title: str,
    ) -> None:
        """docstring"""
        self.figure.suptitle(f'Treatment curve for treatment {title}')
        self.update_plot()

    def update_division_curve(
            self,
            division_curve: dict[str, str | float],
    ) -> None:
        """docstring"""
        self.division_ys = self.get_curve_values(params=division_curve)
        self.update_plot()

    def update_death_curve(
            self,
            death_curve: dict[str, str | float],
    ) -> None:
        """docstring"""
        self.death_ys = self.get_curve_values(params=death_curve)
        self.update_plot()

    def get_curve_values(
            self,
            params: dict[str, str | float],
    ) -> np.ndarray:
        """docstring"""
        curve_name = params.pop('Type')
        curve_function = {
            'Gaussian': norm,
            'EMGaussian': exponnorm,
            'Gamma': gamma,
            'Lognormal': lognorm,
        }[curve_name]
        kwargs = self.translate_scipy_kwargs(input_kwargs=params)
        return curve_function.pdf(self.xs, **kwargs)

    @staticmethod
    def translate_scipy_kwargs(
            input_kwargs
    ) -> dict[str, float]:
        """docstring"""
        kwargs = {
            'loc': input_kwargs.get('Mean'),
            'scale': input_kwargs.get('Std. dev.'),
            'K': input_kwargs.get('K'),
            'a': input_kwargs.get('a'),
            's': input_kwargs.get('s'),
        }
        return {k: v for k, v in kwargs.items() if v is not None}


class NewTreatmentWidget(qtw.QWidget):
    """Widget representing a window where the user can create a new Treatment."""
    def __init__(
            self,
            parent: qtw.QWidget = None,
    ) -> None:
        """Initializes a NewTreatmentWidget instance."""
        super().__init__(parent=parent)

        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        self.treatment_controller = NewTreatmentController()
        layout.addWidget(self.treatment_controller)

        self.treatment_view = NewTreatmentView(
            initial_division_curve=self.treatment_controller.get_division_curve(),
            initial_death_curve=self.treatment_controller.get_death_curve(),
        )
        layout.addWidget(self.treatment_view)

        self.setup()

    def setup(self) -> None:
        """docstring."""
        self.treatment_controller.treatmentNameChanged.connect(self.treatment_view.update_plot_title)
        self.treatment_controller.divisionCurveChanged.connect(self.treatment_view.update_division_curve)
        self.treatment_controller.deathCurveChanged.connect(self.treatment_view.update_death_curve)
        self.treatment_controller.saveTreatmentRequested.connect(self.on_save_treatment_requested)
        self.treatment_controller.loadTreatmentRequested.connect(self.on_load_treatment_requested)
        self.treatment_controller.cancelTreatmentRequested.connect(self.on_cancel_treatment_requested)

        self.treatment_controller.line_edit.setText('TMZ')
        self.treatment_controller.division_curve_widget.combobox.setCurrentText('Gaussian')
        self.treatment_controller.death_curve_widget.combobox.setCurrentText('EMGaussian')

    def on_save_treatment_requested(
            self,
            treatment: dict[str, Any],
    ) -> None:
        """Writes the selected Treatment to a JSON file. Triggered when the "Save Treatment" button is clicked."""
        file_handler = FileHandler(parent=self)
        file_handler.write_treatment(treatment_dict=treatment)

    def on_load_treatment_requested(self) -> None:
        """
        Loads the selected Treatment (JSON file) onto the interface.
        Triggered when the "Load Treatment" button is clicked.
        """
        file_handler = FileHandler(parent=self)
        data = file_handler.load_treatment()
        if data is None:
            return
        self.treatment_controller.load_from_json(json_dict=data)

    def on_cancel_treatment_requested(self) -> None:
        """Asks the user to confirm, then returns to the previous screen."""
        answer = qtw.QMessageBox.question(  # does not work with keyword arguments!
            self,
            'Cancel Treatment',
            'Cancel creating the new treatment? Unsaved changes will be lost.',
        )
        if answer == qtw.QMessageBox.Yes:
            self.close()


def test_loop():
    """Tests the curve_selector_widget.py script."""
    app = qtw.QApplication(sys.argv)
    window = NewTreatmentWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test_loop()
