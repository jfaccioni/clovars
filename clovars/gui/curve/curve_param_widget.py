from __future__ import annotations

import sys
from dataclasses import dataclass

from PySide6 import QtCore as qtc, QtWidgets as qtw

VALID_CURVE_NAMES = ['Gaussian', 'EMGaussian', 'Gamma', 'Lognormal']


@dataclass
class CurveParamModel:
    """Class holding information of a Parameter, including its name, value, and max/min/step."""
    name: str = 'CurveParam'
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


class CurveParamWidget(qtw.QWidget):
    """Widget holding a CurveParam."""
    def __init__(
            self,
            model: CurveParamModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CurveParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or CurveParamModel()

        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        self.label = qtw.QLabel(self.model.name)
        layout.addWidget(self.label)

        self.spinbox = qtw.QDoubleSpinBox(**self.model.to_spinbox())
        layout.addWidget(self.spinbox)

        self.setup()

    def setup(self) -> None:
        """Sets up the connections and the default appearance of the CurveParamWidget."""
        self.spinbox.valueChanged.connect(self.on_spinbox_value_changed)  # noqa

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
        self.spinbox.setValue(new_value)

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)


def get_curve_params(curve_name: str) -> list[CurveParamModel] | None:
    """Returns a list of ParamModel instances, given the curve name (returns None if the name is invalid)."""
    if curve_name not in VALID_CURVE_NAMES:
        return None
    return {
        'Gaussian': [
            CurveParamModel(name='Mean', value=18.0, minimum=0.0, maximum=1_000.0, step=0.5),
            CurveParamModel(name='Std. dev.', value=2.0, minimum=0.0, maximum=1_000_000.0, step=0.5),
        ],
        'EMGaussian': [
            CurveParamModel(name='Mean', value=18.0, minimum=0.0, maximum=1_000.0, step=0.5),
            CurveParamModel(name='Std. dev.', value=2.0, minimum=0.0, maximum=1_000_000.0, step=0.5),
            CurveParamModel(name='K', value=2.0, minimum=0.0, maximum=1_000.0, step=0.5),
        ],
        'Gamma': [
            CurveParamModel(name='Mean', value=18.0, minimum=0.0, maximum=1_000.0, step=0.5),
            CurveParamModel(name='Std. dev.', value=2.0, minimum=0.0, maximum=1_000_000.0, step=0.5),
            CurveParamModel(name='a', value=2.0, minimum=0.0, maximum=1_000.0, step=0.5),
        ],
        'Lognormal': [
            CurveParamModel(name='Mean', value=18.0, minimum=0.0, maximum=1_000.0, step=0.5),
            CurveParamModel(name='Std. dev.', value=2.0, minimum=0.0, maximum=1_000_000.0, step=0.5),
            CurveParamModel(name='s', value=2.0, minimum=0.0, maximum=1_000.0, step=0.5),
        ],
    }[curve_name]


def test_loop():
    """Tests the param_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = CurveParamWidget()
    _add_show_model_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui.gui_utils import _add_show_model_button, _wrap_in_window
    test_loop()
