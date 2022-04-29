from __future__ import annotations

import sys
from dataclasses import dataclass

from PySide6 import QtCore as qtc, QtWidgets as qtw


@dataclass
class FitnessMemorySelectorModel:
    """Class holding information of a FitnessMemory"""
    value: float | None = 0.0
    _min: float = 0.0
    _max: float = 1.0

    def __post_init__(self) -> None:
        """Checks if the value is between the proper values."""
        if self.value is not None and not self._min <= self.value <= self._max:
            raise ValueError(f'Fitness memory must be a value between {self._min} and {self._max}.')

    def to_spinbox(self) -> dict[str, float]:
        """Returns the arguments required by a QCheckBox."""
        return {
            'value': self.value,
            'minimum': self._min,
            'maximum': self._max,
            'singleStep': 0.05,
        }


class FitnessMemorySelectorWidget(qtw.QWidget):
    """Widget used to select a FitnessMemory value."""
    def __init__(
            self,
            adjust_margins: bool = False,
            model: FitnessMemorySelectorModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a ParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or FitnessMemorySelectorModel()

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.checkbox = qtw.QCheckBox('Treatment changes fitness memory?')
        layout.addWidget(self.checkbox)

        self.spinbox = qtw.QDoubleSpinBox(**self.model.to_spinbox())
        layout.addWidget(self.spinbox)

        self.setup()
        if adjust_margins is True:
            self.adjust_layout_margins()

    def setup(self) -> None:
        """Sets up the default appearance of the FitnessMemorySelectorWidget."""
        self.checkbox.toggled.connect(self.on_checkbox_toggled)  # noqa
        self.spinbox.valueChanged.connect(self.on_spinbox_value_changed)  # noqa
        self.checkbox.toggled.emit(False)  # starts the GUI with the checkbox off, sets model value to None  # noqa

    def on_checkbox_toggled(
            self,
            checked: bool,
    ) -> None:
        """Method called when the checkbox is toggled."""
        self.spinbox.setEnabled(checked)
        self.model.value = self.spinbox.value() if checked is True else None

    def on_spinbox_value_changed(
            self,
            new_value: float,
    ) -> None:
        """Method called when the value in the spinbox is changed."""
        self.model.value = new_value

    def get_value(self) -> float:
        """Returns the parameters on the interface."""
        return self.model.value

    def display_value(self) -> None:
        """Prints the parameters from the interface."""
        print(self.get_value())

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)


def test_loop():
    """Tests the fitness_memory_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = FitnessMemorySelectorWidget()
    _add_show_value_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui import _add_show_value_button, _wrap_in_window
    test_loop()
