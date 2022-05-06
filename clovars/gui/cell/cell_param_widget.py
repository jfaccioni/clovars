from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, Any

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.signal import SignalSelectorWidget


@dataclass
class CellParametersModel:
    """Class holding information of Cell Parameters."""
    radius: float = 20.0
    max_speed: float = 10.0
    fitness_memory: float = 0.5
    _min: float = 0.0
    _max: float = 1.0

    def __post_init__(self) -> None:
        """Checks if the value is between the proper values."""
        if not self._min <= self.radius:
            raise ValueError(f'Cell radius cannot be smaller than {self._min}.')
        if not self._min <= self.max_speed:
            raise ValueError(f'Cell max speed cannot be smaller than {self._min}.')
        if not self._min <= self.fitness_memory <= self._max:
            raise ValueError(f'Cell fitness memory must be a value between {self._min} and {self._max}.')

    def __iter__(self) -> Iterator:
        """Iterates over each parameter and its corresponding spinbox dictionary."""
        return iter(zip(
            ['Radius (µm)', 'Max Speed (µm/s)', 'Fitness Memory'],
            [self.radius_slot, self.max_speed_slot, self.fitness_memory_slot],
            [self.to_radius_spinbox(), self.to_max_speed_spinbox(), self.to_fitness_memory_spinbox()],
        ))

    def get_value(self) -> dict[str, float]:
        """Returns a dictionary of the parameters in the CellParametersModel."""
        return {
            'radius': self.radius,
            'max_speed': self.max_speed,
            'fitness_memory': self.fitness_memory,
        }

    @qtc.Slot(float)
    def radius_slot(
            self,
            new_radius_value: float,
    ) -> None:
        """Slot used to update the radius value."""
        self.radius = new_radius_value

    def to_radius_spinbox(self) -> dict[str, float]:
        """Returns the cell radius values as required by a QDoubleSpinBox."""
        return {
            'value': self.radius,
            'minimum': self._min,
            'maximum': 1_000.0,
            'singleStep': 1.0,
        }

    @qtc.Slot(float)
    def max_speed_slot(
            self,
            new_max_speed_value: float,
    ) -> None:
        """Slot used to update the max speed value."""
        self.max_speed = new_max_speed_value

    def to_max_speed_spinbox(self) -> dict[str, float]:
        """Returns the cell max speed values as required by a QDoubleSpinBox."""
        return {
            'value': self.max_speed,
            'minimum': self._min,
            'maximum': 1_000.0,
            'singleStep': 1.0,
        }

    @qtc.Slot(float)
    def fitness_memory_slot(
            self,
            new_fitness_memory_value: float,
    ) -> None:
        """Slot used to update the fitness memory value."""
        self.fitness_memory = new_fitness_memory_value

    def to_fitness_memory_spinbox(self) -> dict[str, float]:
        """Returns the cell fitness memory values as required by a QDoubleSpinBox."""
        return {
            'value': self.fitness_memory,
            'minimum': self._min,
            'maximum': self._max,
            'singleStep': 0.05,
        }


class CellParametersWidget(qtw.QWidget):
    """Widget holding a CellParam."""
    def __init__(
            self,
            model: CellParametersModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CurveParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or CellParametersModel()

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        for label, slot, spinbox_dict in self.model:
            row_layout = qtw.QHBoxLayout()
            layout.addLayout(row_layout)
            label = qtw.QLabel(label)
            row_layout.addWidget(label)
            spinbox = qtw.QDoubleSpinBox(**spinbox_dict)
            spinbox.valueChanged.connect(slot)  # noqa
            row_layout.addWidget(spinbox)

        self.signal_widget = SignalSelectorWidget(widget_type='colony')
        self.signal_widget.set_current_signal(signal_name='Gaussian')
        layout.addWidget(self.signal_widget)

    def get_value(self) -> dict[str, Any]:
        """Returns the parameter's name."""
        params = self.model.get_value()
        params['signal'] = self.signal_widget.get_value()  # noqa
        return params

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.signal_widget.adjust_layout_margins()


def test_loop():
    """Tests the param_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = CellParametersWidget()
    _add_get_value_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui.gui_utils import _add_get_value_button, _wrap_in_window
    test_loop()
