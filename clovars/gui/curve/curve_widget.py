from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.param import CurveParamWidget, get_curve_params

if TYPE_CHECKING:
    from clovars.gui.param import ParamModel


@dataclass
class CurveModel:
    """Class holding information of a Curve, including its name and parameters."""
    name: str = 'Gaussian'
    param_models: list[ParamModel] = None

    def __post_init__(self) -> None:
        """Sets up the params list, given the CellSignal name."""
        self.param_models = get_curve_params(curve_name=self.name)

    def __iter__(self) -> Iterator[ParamModel]:
        """Implements iteration over CellSignalModels by iterating over their list of ParamModels."""
        return iter(self.param_models)


class CurveWidget(qtw.QWidget):
    """Widget holding Curve visualization."""
    def __init__(
            self,
            curve_name: str = None,
            model: CurveModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CellSignalWidget instance."""
        super().__init__(parent=parent)
        self.validate_name_and_model(curve_name=curve_name, model=model)

        self.model = model or CurveModel(name=curve_name)

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.param_widgets = []
        for param_model in self.model:
            param_widget = CurveParamWidget(model=param_model)
            layout.addWidget(param_widget)
            self.param_widgets.append(param_widget)

    @staticmethod
    def validate_name_and_model(
            curve_name: str | None,
            model: CurveModel | None,
    ) -> None:
        """Raises a ValueError if both the name and model are None, or if they both are NOT None."""
        if curve_name is None and model is None:
            raise ValueError('Cannot instantiate CurveModel if both the model and the name are None')
        if curve_name is not None and model is not None:
            raise ValueError('Cannot instantiate CurveModel by providing both the model and the name (either/or)')


def test_loop():
    """Tests the curve_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widgets = []
    curve_names = ['Gaussian', 'EMGaussian', 'Gamma', 'Lognormal', 'EMGaussian']
    for curve_name in curve_names:
        widget = CurveWidget(curve_name=curve_name)
        _add_show_model_button(widget=widget)
        widgets.append(widget)

    window = _wrap_many_in_window(widgets=widgets, orientation='horizontal')
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui import _add_show_model_button, _wrap_many_in_window
    test_loop()
