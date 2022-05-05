from __future__ import annotations

import sys
from dataclasses import dataclass

from PySide6 import QtCore as qtc, QtWidgets as qtw

VALID_SIGNAL_NAMES = ['Sinusoidal', 'Stochastic', 'SinusoidalStochastic', 'Gaussian', 'EMGaussian', 'Constant']


@dataclass
class SignalParamModel:
    """Class holding information of a Parameter, including its name, value, and max/min/step."""
    name: str = 'SignalParam'
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

    def is_empty(self) -> bool:
        """Returns whether the SignalParam is considered "empty" (i.e. its value is None)."""
        return self.value is None


class SignalParamWidget(qtw.QWidget):
    """Widget holding a SignalParam."""
    def __init__(
            self,
            model: SignalParamModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or SignalParamModel()

        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        self.checkbox = qtw.QCheckBox(self.model.name)
        layout.addWidget(self.checkbox)

        self.spinbox = qtw.QDoubleSpinBox(**self.model.to_spinbox())
        layout.addWidget(self.spinbox)

        self.setup()

    def setup(self) -> None:
        """Sets up the connections and the default appearance of the SignalParamWidget."""
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

    def get_name(self) -> str:
        """Returns the parameter's name."""
        return self.model.name

    def load_from_json(
            self,
            json_dict: dict,
    ) -> None:
        """Sets values on the interface from a properly-formatted JSON dictionary."""
        new_value = json_dict[self.get_name()]
        if new_value is None:
            self.checkbox.setChecked(False)
        else:
            self.checkbox.setChecked(True)
            self.spinbox.setValue(new_value)

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)


def get_signal_params(signal_name: str) -> list[SignalParamModel] | None:
    """Returns a list of ParamModel instances, given the signal name (returns None if the name is invalid)."""
    if signal_name not in VALID_SIGNAL_NAMES:
        return None
    return {
        'Sinusoidal': [
            SignalParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            SignalParamModel(name='Period', value=3600.0, minimum=1.0, maximum=1_000_000.0, step=300),
        ],
        'Stochastic': [
            SignalParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            SignalParamModel(name='Noise', value=0.2, minimum=0.0, maximum=1.0, step=0.05),
        ],
        'SinusoidalStochastic': [
            SignalParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            SignalParamModel(name='Period', value=3600.0, minimum=1.0, maximum=1_000_000.0, step=300),
            SignalParamModel(name='Noise', value=0.2, minimum=0.0, maximum=1.0, step=0.05),
        ],
        'Gaussian': [
            SignalParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            SignalParamModel(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05),
            SignalParamModel(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05),
        ],
        'EMGaussian': [
            SignalParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            SignalParamModel(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05),
            SignalParamModel(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05),
            SignalParamModel(name='K', value=0.01, minimum=0.0, maximum=100.0, step=0.05),
        ],
        'Constant': [
            SignalParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
        ],
    }[signal_name]


def test_loop():
    """Tests the param_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = SignalParamWidget()
    _add_show_model_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui.gui_utils import _add_show_model_button, _wrap_in_window
    test_loop()
