from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.signal import SignalParamWidget, get_signal_params

if TYPE_CHECKING:
    from clovars.gui.signal import SignalParamModel


@dataclass
class CellSignalModel:
    """Class holding information of a CellSignal, including its name and parameters."""
    name: str = 'Gaussian'
    param_models: list[SignalParamModel] = None

    def __post_init__(self) -> None:
        """Sets up the params list, given the CellSignal name."""
        self.param_models = get_signal_params(signal_name=self.name)

    def __iter__(self) -> Iterator[SignalParamModel]:
        """Implements iteration over CellSignalModels by iterating over their list of ParamModels."""
        return iter(self.param_models)

    def is_empty(self) -> bool:
        """Returns whether the CellSignal is considered "empty" (i.e. all of its parameters are empty)."""
        return all(param.is_empty() for param in self)


class CellSignalWidget(qtw.QWidget):
    """Widget holding CellSignal visualization."""
    def __init__(
            self,
            widget_type: str = 'treatment',
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
            param_widget = SignalParamWidget(widget_type=widget_type, model=param_model)
            layout.addWidget(param_widget)
            self.param_widgets.append(param_widget)

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

    def load_from_json(
            self,
            json_dict: dict,
    ) -> None:
        """Sets values on the interface from a properly-formatted JSON dictionary."""
        for param_widget in self.param_widgets:
            param_widget.load_from_json(json_dict=json_dict)

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addStretch()
        for param_widget in self.param_widgets:
            param_widget.adjust_layout_margins()


def test_loop(signal_names: list[str]):
    """Tests the cell_signal_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widgets = []
    for signal_name in signal_names:
        widget = CellSignalWidget(signal_name=signal_name)
        _add_show_model_button(widget=widget)
        widgets.append(widget)

    window = _wrap_many_in_window(widgets=widgets, orientation='horizontal')
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui.gui_utils import _add_show_model_button, _wrap_many_in_window
    from clovars.gui.signal import VALID_SIGNAL_NAMES
    test_loop(signal_names=VALID_SIGNAL_NAMES)
