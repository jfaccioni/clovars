from __future__ import annotations

import sys
from dataclasses import dataclass

from PySide6 import QtCore as qtc, QtWidgets as qtw


@dataclass
class ParamModel:
    """Class holding information of a Parameter, including its name, value, and max/min/step."""
    name: str = 'Param'
    value: float | None = 5.0
    minimum: float = 0.0
    maximum: float = 10.0
    step: float = 1.0

    def to_spinbox(self) -> dict[str, float]:
        """Returns the values as expected by a PySide spinbox."""
        return {
            'value': self.value,
            'minimum': self.minimum,
            'maximum': self.maximum,
            'singleStep': self.step,
        }

    def as_signal_param(self) -> dict[str, float]:
        """Returns the values as expected by a clovars CellSignal."""
        return {
            self.name: self.value,
        }

    def is_empty(self) -> bool:
        """Returns whether the Param is considered "empty" (i.e. its value is None)."""
        return self.value is None


class SignalParamWidget(qtw.QWidget):
    """Widget holding Parameter visualization for CellSignals."""
    def __init__(
            self,
            model: ParamModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or ParamModel()

        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        self.checkbox = qtw.QCheckBox(self.model.name)
        layout.addWidget(self.checkbox)

        self.spinbox = qtw.QDoubleSpinBox(**self.model.to_spinbox())
        layout.addWidget(self.spinbox)

        self.setup()

    def setup(self) -> None:
        """Sets up the default appearance of the ParamWidget."""
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


class CurveParamWidget(qtw.QWidget):
    """Widget holding Parameter visualization for Curves."""
    def __init__(
            self,
            model: ParamModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CurveParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or ParamModel()

        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        self.label = qtw.QLabel(self.model.name)
        layout.addWidget(self.label)

        self.spinbox = qtw.QDoubleSpinBox(**self.model.to_spinbox())
        layout.addWidget(self.spinbox)

        self.setup()

    def setup(self) -> None:
        """Sets up the default appearance of the ParamWidget."""
        self.spinbox.valueChanged.connect(self.on_spinbox_value_changed)  # noqa

    def on_spinbox_value_changed(
            self,
            new_value: float,
    ) -> None:
        """Method called when the value in the spinbox is changed."""
        self.model.value = new_value


def test_loop():
    """Tests the param_widget.py script."""
    app = qtw.QApplication(sys.argv)
    model = ParamModel()
    # widget = SignalParamWidget(model=model)
    widget = CurveParamWidget(model=model)
    _add_show_model_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui import _add_show_model_button, _wrap_in_window
    test_loop()
