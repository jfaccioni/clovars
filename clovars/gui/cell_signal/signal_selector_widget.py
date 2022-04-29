from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.param import VALID_SIGNAL_NAMES
from clovars.gui.cell_signal import CellSignalModel, CellSignalWidget


@dataclass
class SignalSelectorModel:
    """Class used to manage multiple CellSignalModels."""
    signal_models: list[CellSignalModel] = None

    def __post_init__(self):
        self.signal_models = [CellSignalModel(name=signal_name) for signal_name in VALID_SIGNAL_NAMES]

    def __iter__(self) -> Iterator[CellSignalModel]:
        """Implements iteration over SignalSelectorModels by iterating over their list of CellSignalModels."""
        return iter(self.signal_models)

    def __getitem__(
            self,
            item: int,
    ) -> CellSignalModel:
        """Implements getitem syntax for SignalSelectorModels by returning the i-th indexed CellSignalModel."""
        if not isinstance(item, int):
            raise ValueError(f"Invalid item type: {item.__class__.__name__} (expected int)")
        return self.signal_models[item]


class SignalSelectorWidget(qtw.QWidget):
    """Widget used to manage multiple CellSignalWidgets."""
    def __init__(
            self,
            adjust_margins: bool = False,
            model: SignalSelectorModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalSelectorWidget instance."""
        super().__init__(parent=parent)

        self.model = model or SignalSelectorModel()

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.checkbox = qtw.QCheckBox("Treatment changes cell signal?")
        layout.addWidget(self.checkbox)

        self.combobox = qtw.QComboBox()
        layout.addWidget(self.combobox)

        self.stack = qtw.QStackedWidget()
        layout.addWidget(self.stack)

        self.signal_widgets = []
        for signal_model in self.model:
            self.combobox.addItem(signal_model.name)
            signal_widget = CellSignalWidget(model=signal_model)
            self.stack.addWidget(signal_widget)
            self.signal_widgets.append(signal_widget)

        self.setup()
        if adjust_margins is True:
            self.adjust_layout_margins()

    def setup(self) -> None:
        """Sets up the default appearance of the SignalSelectorWidget."""
        self.combobox.currentIndexChanged.connect(self.stack.setCurrentIndex)  # noqa
        self.checkbox.stateChanged.connect(self.stack.setEnabled)  # noqa
        self.checkbox.stateChanged.connect(self.combobox.setEnabled)  # noqa
        for signal_widget in self.signal_widgets:
            self.checkbox.toggled.connect(signal_widget.setEnabled)  # noqa
        self.checkbox.toggled.emit(False)  # starts the GUI with the checkbox off, disables widgets  # noqa

    def get_value(self) -> dict | None:
        """Returns the parameters on the interface."""
        current_index = self.combobox.currentIndex()
        current_signal = self.model[current_index]
        if current_signal.is_empty():
            return None
        curve_params = {param.name: param.value for param in current_signal.param_models}
        curve_params['Type'] = current_signal.name
        return curve_params

    def display_value(self) -> None:
        """Prints the parameters from the interface."""
        print(self.get_value())

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addStretch()
        for signal_widget in self.signal_widgets:
            signal_widget.layout().setContentsMargins(0, 0, 0, 0)
            signal_widget.layout().setSpacing(0)
            signal_widget.layout().addStretch()
            for param_widget in signal_widget.param_widgets:
                param_widget.layout().setContentsMargins(0, 0, 0, 0)
                param_widget.layout().setSpacing(0)
                param_widget.layout().addStretch()


def test_loop():
    """Tests the signal_selector_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = SignalSelectorWidget()
    _add_show_value_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui import _add_show_value_button, _wrap_in_window
    test_loop()
