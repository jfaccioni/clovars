from __future__ import annotations

import sys
from functools import partial

import numpy as np
from PySide6 import QtCore as qtc, QtWidgets as qtw
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.stats import norm, exponnorm, gamma, lognorm
import seaborn as sns

sns.set()


class NewTreatmentWindow(qtw.QWidget):
    def __init__(
            self,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a NewTreatmentWindow instance."""
        super().__init__(parent=parent)
        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        self.treatment_params = TreatmentParamsWidget()
        layout.addWidget(self.treatment_params)
        self.treatment_canvas = TreatmentCanvasWidget()
        layout.addWidget(self.treatment_canvas)

        self.treatment_params.paramsChanged.connect(self.treatment_canvas.draw_treatment)


class TreatmentParamsWidget(qtw.QWidget):
    """Widget containing the Treatment parameters."""
    paramsChanged = qtc.Signal(str, str, dict)

    def __init__(
            self,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a TreatmentParamsWidget instance."""
        super().__init__(parent=parent)
        layout = qtw.QGridLayout()
        self.setLayout(layout)

        self.treatment_name_label = qtw.QLabel('Treatment Name: ')
        layout.addWidget(self.treatment_name_label, 0, 0, 1, 1)
        self.line_edit = qtw.QLineEdit()
        layout.addWidget(self.line_edit, 0, 1, 1, 3)
        self.division_curve_widget = CurveParamsWidget(label='Division Curve')
        layout.addWidget(self.division_curve_widget, 1, 0, 1, 2)

        self.death_curve_widget = CurveParamsWidget(label='Death Curve')
        layout.addWidget(self.death_curve_widget, 1, 2, 1, 2)

        layout.setRowStretch(2, 1)

        self.division_curve_widget.paramsChanged.connect(partial(self.on_curve_params_changed, 'Division'))
        self.death_curve_widget.paramsChanged.connect(partial(self.on_curve_params_changed, 'Death'))

    def on_curve_params_changed(
            self,
            label: str,
            curve_name: str,
            curve_params: dict,
    ) -> None:
        """Emits a signal whenever the current params of one of the curves has changed."""
        self.paramsChanged.emit(label, curve_name, curve_params)


class CurveParamsWidget(qtw.QWidget):
    """Widget containing the Curve parameters."""
    paramsChanged = qtc.Signal(str, dict)
    curves = {
        'Gaussian': {
            'mean': 18.0,
            'std': 1.0,
        },
        'EMGaussian': {
            'K': 1.0,
            'mean': 18.0,
            'std': 1.0,
        },
        'Gamma': {
            'a': 1.0,
            'mean': 18.0,
            'std': 1.0,
        },
        'Lognormal': {
            's': 1.0,
            'mean': 18.0,
            'std': 1.0,
        },
    }

    def __init__(
            self,
            label: str = '',
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a CurveParamsWidget instance."""
        super().__init__(parent=parent)
        layout = qtw.QGridLayout()
        self.setLayout(layout)

        self.top_label = qtw.QLabel(label)
        layout.addWidget(self.top_label, 0, 0, 1, 2)

        self.curve_label = qtw.QLabel('Curve Type: ')
        layout.addWidget(self.curve_label, 1, 0, 1, 1)

        self.curve_combobox = qtw.QComboBox()
        layout.addWidget(self.curve_combobox, 1, 1, 1, 1)

        self.curve_name = qtw.QLabel("")
        layout.addWidget(self.curve_name, 2, 0, 1, 2)

        layout.setRowStretch(3, 1)

        self.curve_data = qtw.QFormLayout()
        layout.addLayout(self.curve_data, 3, 0, 1, 2)

        self.curve_combobox.currentTextChanged.connect(self.on_current_text_changed)  # noqa
        self.curve_combobox.addItems(self.curves.keys())  # noqa

    def on_current_text_changed(
            self,
            current_text: str,
    ) -> None:
        """Changes to the appropriate parameters whenever the current text in the combobox changes."""
        self.curve_name.setText(f'{current_text} Params:')
        self.clear_curve_data()
        for key, value in self.curves[current_text].items():
            spinbox = qtw.QDoubleSpinBox()
            spinbox.setValue(value)
            spinbox.valueChanged.connect(partial(self.on_spinbox_value_changed, current_text, key))  # noqa
            self.curve_data.addRow(key, spinbox)

    def on_spinbox_value_changed(
            self,
            current_text: str,
            key: str,
            new_value: float) -> None:
        """Updates the curve data with the new value."""
        self.curves[current_text][key] = new_value
        self.paramsChanged.emit(current_text, self.curves[current_text])

    def clear_curve_data(self) -> None:
        """Removed all widgets from the QFormLayout where the curve data is displayed."""
        # Adapted from: https://stackoverflow.com/a/10067548/11161432
        while self.curve_data.count():
            child = self.curve_data.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class TreatmentCanvasWidget(qtw.QWidget):
    """Widget containing the Treatment canvas."""
    division_curve = {
        'xs': np.array([]),
        'ys': np.array([]),
    }
    death_curve = {
        'xs': np.array([]),
        'ys': np.array([]),
    }

    def __init__(
            self,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a TreatmentCanvasWidget instance."""
        super().__init__(parent=parent)

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure(figsize=(8, 4))
        self.figure.suptitle('Treatment Curves')

        self.ax = self.figure.subplots()

        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def draw_treatment(
            self,
            label: str,
            curve_name: str,
            curve_params: dict,
    ) -> None:
        """Draws the treatment onto the canvas."""
        curve_params = curve_params.copy()  # do not mess with the original dict when popping values
        curve_data = self.division_curve if label == 'Division' else self.death_curve
        curve_data['xs'] = np.linspace(0, 300, 10_000)
        curve_data['ys'] = {
            'Gaussian': norm,
            'EMGaussian': exponnorm,
            'Gamma': gamma,
            'Lognormal': lognorm,
        }[curve_name].pdf(curve_data['xs'], loc=curve_params.pop('mean'), scale=curve_params.pop('std'), **curve_params)
        self.ax.clear()
        self.ax.plot(self.division_curve['xs'], self.division_curve['ys'], label='Division curve', color='#029e73')
        self.ax.plot(self.death_curve['xs'], self.death_curve['ys'], label='Death curve', color='#de8f05')
        self.ax.legend()
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Density')
        self.figure.tight_layout()
        self.canvas.draw()


def mainloop() -> None:
    """Executes the main loop on the GUI."""
    app = qtw.QApplication(sys.argv)
    main_window = NewTreatmentWindow()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    mainloop()
