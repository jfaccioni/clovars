from __future__ import annotations

import sys

import seaborn as sns
from PySide6 import QtCore as qtc, QtWidgets as qtw

sns.set()


class CellSignalController(qtw.QWidget):
    signalSent = qtc.Signal(dict)

    def __init__(
            self,
            label: str = '',
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a CellSignalController instance."""
        super().__init__(parent=parent)

        # LAYOUT
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # CHECKBOX TOGGLING VIEW STATE
        self.view_combobox = qtw.QCheckBox(label)
        layout.addWidget(self.view_combobox)

        # MODEL AND VIEW
        self.model = CellSignalModel()
        self.view = CellSignalView(initial_data=self.model.data, signal_limits=self.model.signal_limits)
        layout.addWidget(self.view)

        self.set_up()

    def set_up(self) -> None:
        """Sets up the default widget appearance and its internal connections."""
        # APPEARANCE
        self.view_combobox.setChecked(False)
        self.view.setEnabled(False)

        # CONNECTIONS
        self.view_combobox.stateChanged.connect(self.view.setEnabled)  # noqa

    def send_data(self) -> dict:
        """Sends the signal data."""
        print(self.model.signal)  # TODO: replace with signal being emitted
        return self.model.signal


class CellSignalModel(qtc.QObject):
    """Class representing the model containing the CellSignal data."""
    signal_limits = {
        'initial value': {
            'minimum': -1.0,
            'maximum': 1.0,
            'single_step': 0.05,
        },
        'period': {
            'minimum': 1.0,
            'maximum': 1_000_000.0,
            'single_step': 300.0,
        },
        'noise': {
            'minimum': 0.0,
            'maximum': 1.0,
            'single_step': 0.05,
        },
        'mean': {
            'minimum': -100.0,
            'maximum': 100.0,
            'single_step': 0.05,
        },
        'std': {
            'minimum': 0.0,
            'maximum': 100.0,
            'single_step': 0.05,
        },
        'k': {
            'minimum': 0.0,
            'maximum': 100.0,
            'single_step': 0.05,
        },
    }

    def __init__(self) -> None:
        super().__init__()
        self.selected_signal = ''
        self.data = {
            'Sinusoidal': {
                'initial value': 0.0,
                'period': 3600,
            },
            'Stochastic': {
                'initial value': 0.0,
                'noise': 0.2,
            },
            'Stoch. + Sin.': {
                'initial value': 0.0,
                'period': 3600,
                'noise': 0.2,
            },
            'Gaussian': {
                'initial value': 0.0,
                'mean': 0.0,
                'std': 0.05,
            },
            'E. M. Gaussian': {
                'initial value': 0.0,
                'k': 0.01,
                'mean': 0.0,
                'std': 0.05,
            },
            'Constant': {
                'initial value': 0.0,
            }
        }

    @property
    def signal(self) -> dict:
        """
        Returns a dictionary of the currently selected signal's parameters.
        The dictionary can be used to build a CellSignal instance.
        """
        params = self.data[self.selected_signal].copy()
        params['name'] = self.selected_signal
        params['initial_value'] = params.pop('initial value')
        return params

    def update_cell_signal_params(
            self,
            signal_name: str,
            param_name: str,
            param_value: float,
    ) -> None:
        """Updates a parameter in one of the CellSignals."""
        self.data[signal_name][param_name] = param_value

    def select_cell_signal(
            self,
            new_cell_signal: str,
    ) -> None:
        """Updates the currently selected CellSignal in the CellSignalModel."""
        self.selected_signal = new_cell_signal


class CellSignalView(qtw.QWidget):  # View
    """Widget containing the CellSignal parameters."""
    cellSignalSelected = qtc.Signal(str)
    paramChanged = qtc.Signal(str, str, object)

    def __init__(
            self,
            initial_data: dict,
            signal_limits: dict,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a CellSignalParamsWidget instance."""
        super().__init__(parent=parent)

        # LAYOUT
        layout = qtw.QFormLayout()
        self.setLayout(layout)

        # ROW 0
        self.signal_label = qtw.QLabel('Signal type: ')
        self.signal_combobox = qtw.QComboBox()
        layout.addRow(self.signal_label, self.signal_combobox)

        # ROW 1
        self.signals_stacked_widget = qtw.QStackedWidget()
        layout.addRow(self.signals_stacked_widget)

        # WIDGETS IN STACKED WIDGET
        for signal_name, signal_params in initial_data.items():
            self.signal_combobox.addItem(signal_name)
            _layout = qtw.QVBoxLayout()
            _widget = qtw.QWidget()
            _widget.setLayout(_layout)
            self.signals_stacked_widget.addWidget(_widget)
            for name, value in signal_params.items():
                limits = signal_limits[name]
                checkable_spinbox = QCheckableSpinBox(label=name, value=value, limits=limits)
                checkable_spinbox.valueChanged.connect(self.on_spinbox_value_changed)
                _layout.addWidget(checkable_spinbox)
            _layout.addStretch()

        # CONNECTIONS
        self.signal_combobox.currentTextChanged.connect(self.cellSignalSelected.emit)  # noqa
        self.signal_combobox.currentIndexChanged.connect(self.signals_stacked_widget.setCurrentIndex)  # noqa

    def on_spinbox_value_changed(
            self,
            value: float,
    ) -> None:
        """docstring"""
        spinbox = self.sender()
        self.paramChanged.emit(self.signal_combobox.currentText(), spinbox.text(), value)
        print(self.signal_combobox.currentText(), spinbox.text(), value)


class QCheckableSpinBox(qtw.QWidget):
    """Widget comprised of a spinbox that can be activated using a checkbox."""
    valueChanged = qtc.Signal(object)

    def __init__(
            self,
            label: str,
            value: float,
            limits: dict,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """docstring"""
        super().__init__(parent=parent)

        # LAYOUT
        layout = qtw.QHBoxLayout()
        self.setLayout(layout)

        # CHECKBOX
        self.checkbox = qtw.QCheckBox(label)
        layout.addWidget(self.checkbox)

        # SPINBOX
        self.spinbox = qtw.QDoubleSpinBox(
            minimum=limits['minimum'],  # noqa
            maximum=limits['maximum'],  # noqa
            value=value,  # noqa
            singleStep=limits['single_step'],  # noqa
        )
        layout.addWidget(self.spinbox)

        # CONNECTIONS
        self.checkbox.stateChanged.connect(self.spinbox.setEnabled)  # noqa
        self.checkbox.stateChanged.connect(lambda state: self.valueChanged.emit(self.spinbox.value()) if state else None)  # noqa
        self.spinbox.valueChanged.connect(self.valueChanged)  # noqa

        # INITIAL SETUP
        self.spinbox.setEnabled(False)

    def text(self) -> str:
        """Returns the text in the checkbox."""
        return self.checkbox.text()


def mainloop() -> None:
    """Executes the main loop on the GUI."""
    app = qtw.QApplication(sys.argv)
    main_window = CellSignalController(label='Activate Signal')
    main_window.show()
    app.exec()


if __name__ == '__main__':
    mainloop()
