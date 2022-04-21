from __future__ import annotations

import sys

import numpy as np
import seaborn as sns
from PySide6 import QtCore as qtc, QtWidgets as qtw
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavBar
from matplotlib.figure import Figure

from clovars.bio import Treatment
from clovars.scientific import Curve, get_curve

sns.set()


class NewTreatmentWindow(qtw.QWidget):  # Main Widget
    def __init__(
            self,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a NewTreatmentWindow instance."""
        super().__init__(parent=parent)

        # MODELS
        self.division_curve_model = CurveModel()
        self.death_curve_model = CurveModel()
        self.cell_signal_model = CellSignalModel()

        # MAIN LAYOUT
        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        # LEFT COLUMN
        left_layout = qtw.QGridLayout()
        layout.addLayout(left_layout)

        # ROW 0
        self.treatment_name_label = qtw.QLabel('Treatment Name: ')
        left_layout.addWidget(self.treatment_name_label, 0, 0, 1, 1)
        self.line_edit = qtw.QLineEdit()
        left_layout.addWidget(self.line_edit, 0, 1, 1, 3)

        # ROW 1
        self.division_curve_controller = CurveParamsWidget(label='Division', data=self.division_curve_model.data)
        left_layout.addWidget(self.division_curve_controller, 1, 0, 1, 2)
        self.death_curve_controller = CurveParamsWidget(label='Death', data=self.death_curve_model.data)
        left_layout.addWidget(self.death_curve_controller, 1, 2, 1, 2)

        # ROW 2
        self.fitness_memory_checkbox = qtw.QCheckBox('Change colony fitness memory', checked=False)  # noqa
        left_layout.addWidget(self.fitness_memory_checkbox, 2, 0, 1, 2)
        self.fitness_memory_spinbox = qtw.QDoubleSpinBox(minimum=0.0, maximum=1.0, value=0.0, singleStep=0.05)  # noqa
        left_layout.addWidget(self.fitness_memory_spinbox, 2, 2, 1, 2)

        # ROW 3
        self.signal_checkbox = qtw.QCheckBox('Change colony signal type', checked=False)  # noqa
        left_layout.addWidget(self.signal_checkbox, 3, 0, 1, 1)
        self.signal_controller = CellSignalParamsWidget(
            data=self.cell_signal_model.data,
            limits=self.cell_signal_model.limits,
        )
        left_layout.addWidget(self.signal_controller, 3, 1, 1, 3)

        # ROW 4
        self.save_button = qtw.QPushButton('Save')
        left_layout.addWidget(self.save_button, 4, 0, 1, 1)

        # ADD STRETCH
        left_layout.setRowStretch(4, 1)

        # RIGHT COLUMN
        self.treatment_view = TreatmentCanvasWidget()
        layout.addWidget(self.treatment_view)

        # CONNECTIONS
        self.connect_widgets()

        # INITIAL STATE
        self.set_initial_state()

    def connect_widgets(self) -> None:
        """docstring"""
        # Updates the models through the controllers
        self.division_curve_controller.curveSelected.connect(self.division_curve_model.select_curve)  # noqa
        self.division_curve_controller.paramChanged.connect(self.division_curve_model.update_curve_params)  # noqa
        self.death_curve_controller.curveSelected.connect(self.death_curve_model.select_curve)  # noqa
        self.death_curve_controller.paramChanged.connect(self.death_curve_model.update_curve_params)  # noqa
        self.signal_controller.cellSignalSelected.connect(self.cell_signal_model.select_cell_signal)  # noqa
        self.signal_controller.paramChanged.connect(self.cell_signal_model.update_cell_signal_params)  # noqa

        # Updates the view through the models
        self.division_curve_model.dataChanged.connect(self.treatment_view.update_division_curve)  # noqa
        self.death_curve_model.dataChanged.connect(self.treatment_view.update_death_curve)  # noqa

        # Updates treatment name in the view
        self.line_edit.textChanged.connect(self.treatment_view.update_plot_title)  # noqa

        # Enables spinboxes based on checkboxes
        self.fitness_memory_checkbox.stateChanged.connect(self.fitness_memory_spinbox.setEnabled)  # noqa
        self.signal_checkbox.stateChanged.connect(self.signal_controller.setEnabled)  # noqa

        # Return from the dialogue with the treatment
        self.save_button.clicked.connect(self.save_treatment)  # noqa

    def set_initial_state(self) -> None:
        """docstring"""
        self.line_edit.setText('TMZ')
        self.fitness_memory_spinbox.setEnabled(False)
        self.signal_controller.setEnabled(False)
        # Only works if the text in the comboboxes isn't the same text being set here - otherwise no signal is emitted
        self.division_curve_controller.curve_combobox.setCurrentText('Gamma')
        self.death_curve_controller.curve_combobox.setCurrentText('EMGaussian')
        self.signal_controller.signal_combobox.setCurrentText('Gaussian')

    def save_treatment(self) -> Treatment:
        """Returns a Treatment instance from the NewTreatmentWindow."""
        fitness_memory_disturbance = None
        if self.fitness_memory_spinbox.isEnabled():
            fitness_memory_disturbance = self.fitness_memory_spinbox.value()
        signal_disturbance = None
        if self.signal_controller.isEnabled():
            signal_disturbance = self.cell_signal_model.signal_disturbance
        treatment = Treatment(
            name=self.line_edit.text(),
            division_curve=self.division_curve_model.curve,
            death_curve=self.death_curve_model.curve,
            fitness_memory_disturbance=fitness_memory_disturbance,
            signal_disturbance=signal_disturbance,
        )
        print(treatment.__dict__)
        return treatment


class CurveModel(qtc.QObject):  # Model
    """Class representing the model containing the Curve data."""
    dataChanged = qtc.Signal(Curve)

    def __init__(self) -> None:
        super().__init__()
        self.selected_curve = 'Gaussian'
        self.data = {
            'Gaussian': {
                'mean': 22.0,
                'std': 3.5,
            },
            'EMGaussian': {
                'k': 2.87,
                'mean': 12.72,
                'std': 8.50,
            },
            'Gamma': {
                'a': 3.32,
                'mean': 16.23,
                'std': 2.84,
            },
            'Lognormal': {
                's': 1.5,
                'mean': 26.0,
                'std': 4.5,
            },
        }

    @property
    def curve(self) -> Curve:
        """Returns a Curve instance of the currently selected curve's parameters."""
        params = self.data[self.selected_curve]
        return get_curve(name=self.selected_curve, **params)

    def update_curve_params(
            self,
            curve_name: str,
            param_name: str,
            param_value: float,
    ) -> None:
        """Updates a parameter in one of the CurveModel's curves."""
        self.data[curve_name][param_name] = param_value
        self.update()

    def select_curve(
            self,
            new_curve: str,
    ) -> None:
        """Updates the currently selected curve in the CurveModel."""
        self.selected_curve = new_curve
        self.update()

    def update(self) -> None:
        """docstring"""
        self.dataChanged.emit(self.curve)


class TreatmentCanvasWidget(qtw.QWidget):  # View
    """Widget containing the Treatment canvas."""
    def __init__(
            self,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a TreatmentCanvasWidget instance."""
        super().__init__(parent=parent)

        # FIGURE AND AXES
        self.figure = Figure(figsize=(8, 4))
        self.ax = self.figure.subplots()

        # DATA
        self.xs = np.linspace(0, 300, 10_000)
        self.division_ys = np.full(self.xs.shape, np.nan)
        self.death_ys = np.full(self.xs.shape, np.nan)

        # LAYOUT
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # CANVAS AND NAVBAR
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.navbar = NavBar(self.canvas, self)
        layout.addWidget(self.navbar)

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
            division_curve: Curve,
    ) -> None:
        """docstring"""
        self.division_ys = division_curve.pdf(self.xs)
        self.update_plot()

    def update_death_curve(
            self,
            death_curve: Curve,
    ) -> None:
        """docstring"""
        self.death_ys = death_curve.pdf(self.xs)
        self.update_plot()


class CurveParamsWidget(qtw.QWidget):  # Controller
    """Widget containing the Curve parameters."""
    curveSelected = qtc.Signal(str)
    paramChanged = qtc.Signal(str, str, float)

    def __init__(
            self,
            label: str,
            data: dict,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a CurveParamsWidget instance."""
        super().__init__(parent=parent)

        # LAYOUT
        layout = qtw.QGridLayout()
        self.setLayout(layout)

        # ROW 0
        self.top_label = qtw.QLabel(f'{label} curve')
        layout.addWidget(self.top_label, 0, 0, 1, 2)

        # ROW 1
        self.curve_label = qtw.QLabel('Curve type: ')
        layout.addWidget(self.curve_label, 1, 0, 1, 1)
        self.curve_combobox = qtw.QComboBox()
        layout.addWidget(self.curve_combobox, 1, 1, 1, 1)

        # ROW 2
        self.curve_name = qtw.QLabel("")
        layout.addWidget(self.curve_name, 2, 0, 1, 2)

        # ROW 3
        self.curves_stacked_widget = qtw.QStackedWidget()
        layout.addWidget(self.curves_stacked_widget, 3, 0, 1, 2)

        # WIDGETS IN STACKED WIDGET
        for curve_type, curve_params in data.items():
            self.curve_combobox.addItem(curve_type)
            form_layout = qtw.QFormLayout()
            widget = qtw.QWidget()
            widget.setLayout(form_layout)
            self.curves_stacked_widget.addWidget(widget)
            for param_name, param_value in curve_params.items():
                spinbox = qtw.QDoubleSpinBox(
                    objectName=f'{curve_type}_{param_name}',  # noqa
                    minimum=0.0,  # noqa
                    maximum=100.0,  # noqa
                    value=param_value,  # noqa
                    singleStep=0.5,  # noqa
                )
                spinbox.valueChanged.connect(self.on_spinbox_value_changed)  # noqa
                form_layout.addRow(param_name, spinbox)

        # ADD STRETCH
        layout.setRowStretch(4, 1)

        # CONNECTIONS
        self.curve_combobox.currentTextChanged.connect(self.curveSelected.emit)  # noqa
        self.curve_combobox.currentIndexChanged.connect(self.curves_stacked_widget.setCurrentIndex)  # noqa

    def on_spinbox_value_changed(
            self,
            new_value: float,
    ) -> None:
        """docstring"""
        curve_type, param_name = self.sender().objectName().split('_')
        self.paramChanged.emit(curve_type, param_name, new_value)


class CellSignalModel(qtc.QObject):  # Model
    """Class representing the model containing the CellSignal data."""
    limits = {
        'initial value': {
            'minimum': -1.0,
            'maximum': 1.0,
            'single_step': 0.05,
        },
        'period': {
            'minimum': 1.0,
            'maximum': 1_000_000.0,
            'single_step': 300.0,
        },
        'noise': {
            'minimum': 0.0,
            'maximum': 1.0,
            'single_step': 0.05,
        },
        'mean': {
            'minimum': -100.0,
            'maximum': 100.0,
            'single_step': 0.05,
        },
        'std': {
            'minimum': 0.0,
            'maximum': 100.0,
            'single_step': 0.05,
        },
        'k': {
            'minimum': 0.0,
            'maximum': 100.0,
            'single_step': 0.05,
        },
    }

    def __init__(self) -> None:
        super().__init__()
        self.selected_cell_signal = 'Sinusoidal'
        self.data = {
            'Sinusoidal': {
                'initial value': 0.0,
                'period': 3600,
            },
            'Stochastic': {
                'initial value': 0.0,
                'noise': 0.2,
            },
            'Stoch + Sin': {
                'initial value': 0.0,
                'period': 3600,
                'noise': 0.2,
            },
            'Gaussian': {
                'initial value': 0.0,
                'mean': 0.0,
                'std': 0.05,
            },
            'EMGaussian': {
                'initial value': 0.0,
                'k': 0.01,
                'mean': 0.0,
                'std': 0.05,
            },
            'Constant': {
                'initial value': 0.0,
            }
        }

    @property
    def signal_disturbance(self) -> dict:
        """Returns a dictionary of the currently selected signal's parameters."""
        params = self.data[self.selected_cell_signal].copy()
        params['name'] = self.selected_cell_signal
        params['initial_value'] = params.pop('initial value')
        return params

    def update_cell_signal_params(
            self,
            cell_signal_name: str,
            param_name: str,
            param_value: float,
    ) -> None:
        """Updates a parameter in one of the CellSignalModel's curves."""
        self.data[cell_signal_name][param_name] = param_value

    def select_cell_signal(
            self,
            new_cell_signal: str,
    ) -> None:
        """Updates the currently selected CellSignal in the CellSignalModel."""
        self.selected_cell_signal = new_cell_signal


class CellSignalParamsWidget(qtw.QWidget):  # Controller
    """Widget containing the CellSignal parameters."""
    cellSignalSelected = qtc.Signal(str)
    paramChanged = qtc.Signal(str, str, float)

    def __init__(
            self,
            data: dict,
            limits: dict,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a CellSignalParamsWidget instance."""
        super().__init__(parent=parent)

        # LAYOUT
        layout = qtw.QGridLayout()
        self.setLayout(layout)

        # ROW 0
        self.curve_label = qtw.QLabel('Signal type: ')
        layout.addWidget(self.curve_label, 0, 0, 1, 1)
        self.signal_combobox = qtw.QComboBox()
        layout.addWidget(self.signal_combobox, 0, 1, 1, 1)

        # ROW 1
        self.signal_name = qtw.QLabel("")
        layout.addWidget(self.signal_name, 1, 0, 1, 2)

        # ROW 2
        self.signals_stacked_widget = qtw.QStackedWidget()
        layout.addWidget(self.signals_stacked_widget, 2, 0, 1, 2)

        # WIDGETS IN STACKED WIDGET
        for signal_type, signal_params in data.items():
            self.signal_combobox.addItem(signal_type)
            form_layout = qtw.QFormLayout()
            widget = qtw.QWidget()
            widget.setLayout(form_layout)
            self.signals_stacked_widget.addWidget(widget)
            for param_name, param_value in signal_params.items():
                spinbox = qtw.QDoubleSpinBox(
                    objectName=f'{signal_type}_{param_name}',  # noqa
                    minimum=limits[param_name]['minimum'],  # noqa
                    maximum=limits[param_name]['maximum'],  # noqa
                    value=param_value,  # noqa
                    singleStep=limits[param_name]['single_step'],  # noqa
                )
                spinbox.valueChanged.connect(self.on_spinbox_value_changed)  # noqa
                form_layout.addRow(param_name, spinbox)

        # ADD STRETCH
        layout.setRowStretch(3, 1)

        # CONNECTIONS
        self.signal_combobox.currentTextChanged.connect(self.cellSignalSelected.emit)  # noqa
        self.signal_combobox.currentIndexChanged.connect(self.signals_stacked_widget.setCurrentIndex)  # noqa

    def on_spinbox_value_changed(
            self,
            new_value: float,
    ) -> None:
        """docstring"""
        signal_type, param_name = self.sender().objectName().split('_')
        self.paramChanged.emit(signal_type, param_name, new_value)


def mainloop() -> None:
    """Executes the main loop on the GUI."""
    app = qtw.QApplication(sys.argv)
    main_window = NewTreatmentWindow()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    mainloop()
