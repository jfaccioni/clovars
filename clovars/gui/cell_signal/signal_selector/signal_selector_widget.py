from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator

from PySide6 import QtCore as qtc, QtWidgets as qtw

from clovars.gui.cell_signal import _VALID_SIGNAL_NAMES, CellSignalModel, CellSignalWidget


@dataclass
class SignalSelectorModel:
    """Class used to manage multiple CellSignalModels."""
    signal_models: list[CellSignalModel] = None

    def __post_init__(self):
        self.signal_models = [CellSignalModel(name=signal_name) for signal_name in _VALID_SIGNAL_NAMES]

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
            model: SignalSelectorModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalSelectorWidget instance."""
        super().__init__(parent=parent)

        self.model = model or SignalSelectorModel()

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.checkbox = qtw.QCheckBox("Add CellSignal disturbance?")
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

        self.button = qtw.QPushButton('Save')
        layout.addWidget(self.button)

        self.setup()

    def setup(self) -> None:
        """Sets up the default appearance of the SignalSelectorWidget."""
        self.combobox.currentIndexChanged.connect(self.stack.setCurrentIndex)  # noqa
        self.checkbox.stateChanged.connect(self.stack.setEnabled)  # noqa
        self.checkbox.stateChanged.connect(self.combobox.setEnabled)  # noqa
        for signal_widget in self.signal_widgets:
            self.checkbox.toggled.connect(signal_widget.setEnabled)  # noqa
        self.checkbox.toggled.emit(False)  # starts the GUI with the checkbox off, disables widgets  # noqa
        self.button.clicked.connect(lambda: print(self.on_button_clicked()))  # noqa

    def on_button_clicked(self) -> dict:
        """Returns the parameters on the interface."""
        current_index = self.combobox.currentIndex()
        current_signal = self.model[current_index]
        return {
            current_signal.name: {param.name: param.value for param in current_signal.param_models}
        }


def test_loop():
    """Tests the signal_selector_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = SignalSelectorWidget()
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui import _add_show_model_button, _wrap_in_window
    test_loop()
