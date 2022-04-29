from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.param import SignalParamWidget, get_signal_params

if TYPE_CHECKING:
    from clovars.gui.param import ParamModel


@dataclass
class CellSignalModel:
    """Class holding information of a CellSignal, including its name and parameters."""
    name: str = 'Gaussian'
    param_models: list[ParamModel] = None

    def __post_init__(self) -> None:
        """Sets up the params list, given the CellSignal name."""
        self.param_models = get_signal_params(signal_name=self.name)

    def __iter__(self) -> Iterator[ParamModel]:
        """Implements iteration over CellSignalModels by iterating over their list of ParamModels."""
        return iter(self.param_models)

    def is_empty(self) -> bool:
        """Returns whether the CellSignal is considered "empty" (i.e. all of its parameters are empty)."""
        return all(param.is_empty() for param in self)


class CellSignalWidget(qtw.QWidget):
    """Widget holding CellSignal visualization."""
    def __init__(
            self,
            signal_name: str = None,
            model: CellSignalModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CellSignalWidget instance."""
        super().__init__(parent=parent)
        self.validate_name_and_model(signal_name=signal_name, model=model)

        self.model = model or CellSignalModel(name=signal_name)

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.param_widgets = []
        for param_model in self.model:
            param_widget = SignalParamWidget(model=param_model)
            layout.addWidget(param_widget)

    @staticmethod
    def validate_name_and_model(
            signal_name: str | None,
            model: CellSignalModel | None,
    ) -> None:
        """Raises a ValueError if both the name and model are None, or if they both are NOT None."""
        if signal_name is None and model is None:
            raise ValueError('Cannot instantiate CellSignalWidget if both the model and the name are None')
        if signal_name is not None and model is not None:
            raise ValueError('Cannot instantiate CellSignalWidget by providing both the model and the name (either/or)')


def test_loop():
    """Tests the cell_signal_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widgets = []
    signal_names = ['Sinusoidal', 'Stochastic', 'SinusoidalStochastic', 'Gaussian', 'EMGaussian', 'Constant']
    for signal_name in signal_names:
        widget = CellSignalWidget(signal_name=signal_name)
        _add_show_model_button(widget=widget)
        widgets.append(widget)

    window = _wrap_many_in_window(widgets=widgets, orientation='horizontal')
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui import _add_show_model_button, _wrap_many_in_window
    test_loop()
