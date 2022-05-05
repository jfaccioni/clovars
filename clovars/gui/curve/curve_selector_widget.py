from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.curve import CurveModel, CurveWidget, VALID_CURVE_NAMES


@dataclass
class CurveSelectorModel:
    """Class used to manage multiple CurveModels."""
    curve_models: list[CurveModel] = None

    def __post_init__(self):
        self.curve_models = [CurveModel(name=curve_name) for curve_name in VALID_CURVE_NAMES]

    def __iter__(self) -> Iterator[CurveModel]:
        """Implements iteration over CurveSelectorModels by iterating over their list of CurveModels."""
        return iter(self.curve_models)

    def __getitem__(
            self,
            item: int,
    ) -> CurveModel:
        """Implements getitem syntax for CurveSelectorModels by returning the i-th indexed CurveModel."""
        if not isinstance(item, int):
            raise ValueError(f"Invalid item type: {item.__class__.__name__} (expected int)")
        return self.curve_models[item]


class CurveSelectorWidget(qtw.QWidget):
    """Widget used to manage multiple CurveWidgets."""
    curveChanged = qtc.Signal(dict)

    def __init__(
            self,
            curve_name: str,
            adjust_margins: bool = False,
            model: CurveModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CurveSelectorWidget instance."""
        super().__init__(parent=parent)

        self.model = model or CurveSelectorModel()

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.label = qtw.QLabel(text=curve_name)
        layout.addWidget(self.label)

        self.combobox = qtw.QComboBox()
        layout.addWidget(self.combobox)

        self.stack = qtw.QStackedWidget()
        layout.addWidget(self.stack)

        self.curve_widgets = []
        for curve_model in self.model:
            self.combobox.addItem(curve_model.name)
            curve_widget = CurveWidget(model=curve_model)
            self.stack.addWidget(curve_widget)
            self.curve_widgets.append(curve_widget)

        self.setup()
        if adjust_margins is True:
            self.adjust_layout_margins()

    def setup(self) -> None:
        """Sets up the connections and the default appearance of the CurveSelectorWidget."""
        self.combobox.currentIndexChanged.connect(self.stack.setCurrentIndex)  # noqa
        self.combobox.currentIndexChanged.connect(self.emit_value)  # noqa
        for curve_widget in self.curve_widgets:
            for param_widget in curve_widget.param_widgets:
                param_widget.spinbox.valueChanged.connect(self.emit_value)

    def get_current_curve(self) -> CurveModel:
        """Returns the CurveModel of the currently selected curve."""
        current_index = self.combobox.currentIndex()
        return self.model[current_index]

    def get_current_curve_widget(self) -> CurveWidget:
        """Returns the CurveWidget of the currently selected curve."""
        current_index = self.combobox.currentIndex()
        return self.curve_widgets[current_index]

    def get_value(self) -> dict:
        """Returns the parameters on the interface."""
        current_curve = self.get_current_curve()
        curve_params = {param.name: param.value for param in current_curve.param_models}
        curve_params['Type'] = current_curve.name
        return curve_params

    def emit_value(self) -> None:
        """Emits the current curve through a signal."""
        self.curveChanged.emit(self.get_value())

    def display_value(self) -> None:
        """Prints the parameters from the interface."""
        print(self.get_value())

    def load_from_json(
            self,
            json_dict: dict,
    ) -> None:
        """Sets values on the interface from a properly-formatted JSON dictionary."""
        self.combobox.setCurrentText(json_dict['Type'])
        current_curve_widget = self.get_current_curve_widget()
        current_curve_widget.load_from_json(json_dict=json_dict)

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        for curve_widget in self.curve_widgets:
            curve_widget.adjust_layout_margins()


def test_loop():
    """Tests the curve_selector_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widgets = []
    for curve_name in ['Division Curve', 'Death Curve']:
        widget = CurveSelectorWidget(curve_name=curve_name)
        _add_show_value_button(widget=widget)
        widgets.append(widget)
    window = _wrap_many_in_window(widgets=widgets, orientation='horizontal')
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui.gui_utils import _add_show_value_button, _wrap_many_in_window
    test_loop()
