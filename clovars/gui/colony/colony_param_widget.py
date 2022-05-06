from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, Any

from PySide6 import QtCore as qtc, QtWidgets as qtw


@dataclass
class ColonyParametersModel:
    """Class holding information of Colony Parameters."""
    copies: int = 1
    initial_size: int = 1
    _min: int = 1

    def __post_init__(self) -> None:
        """Checks if the value is between the proper values."""
        if not self._min <= self.copies:
            raise ValueError(f'Copies cannot be smaller than {self._min}.')
        if not self._min <= self.initial_size:
            raise ValueError(f'Initial size cannot be smaller than {self._min}.')

    def __iter__(self) -> Iterator:
        """Iterates over each parameter and its corresponding spinbox dictionary."""
        return iter(zip(
            ['Number of Copies', 'Initial Colony Size'],
            [self.copies_slot, self.initial_size_slot],
            [self.to_copies_spinbox(), self.to_initial_size_spinbox()],
        ))

    def get_value(self) -> dict[str, float]:
        """Returns a dictionary of the parameters in the CellParametersModel."""
        return {
            'copies': self.copies,
            'initial_size': self.initial_size,
        }

    @qtc.Slot(int)
    def copies_slot(
            self,
            new_copies_value: int,
    ) -> None:
        """Slot used to update the copies value."""
        self.copies = new_copies_value

    def to_copies_spinbox(self) -> dict[str, int]:
        """Returns the copies values as required by a QDoubleSpinBox."""
        return {
            'value': self.copies,
            'minimum': self._min,
            'maximum': 1_000,
            'singleStep': 1,
        }

    @qtc.Slot(int)
    def initial_size_slot(
            self,
            new_initial_size_value: int,
    ) -> None:
        """Slot used to update the initial size value."""
        self.initial_size = new_initial_size_value

    def to_initial_size_spinbox(self) -> dict[str, int]:
        """Returns the colony initial size values as required by a QDoubleSpinBox."""
        return {
            'value': self.initial_size,
            'minimum': self._min,
            'maximum': 1_000,
            'singleStep': 1,
        }


class ColonyParametersWidget(qtw.QWidget):
    """Widget holding a ColonyParam."""
    def __init__(
            self,
            adjust_margins: bool = False,
            model: ColonyParametersModel = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a CurveParamWidget instance."""
        super().__init__(parent=parent)
        self.model = model or ColonyParametersModel()

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        for label, slot, spinbox_dict in self.model:
            row_layout = qtw.QHBoxLayout()
            layout.addLayout(row_layout)
            label = qtw.QLabel(label)
            row_layout.addWidget(label)
            spinbox = qtw.QSpinBox(**spinbox_dict)
            spinbox.valueChanged.connect(slot)  # noqa
            row_layout.addWidget(spinbox)

        if adjust_margins is True:
            self.adjust_layout_margins()

    def get_value(self) -> dict[str, Any]:
        """Returns the parameter's name."""
        params = self.model.get_value()
        return params

    def adjust_layout_margins(self) -> None:
        """Adjusts the margins for all layouts in the widget."""
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)


def test_loop():
    """Tests the param_widget.py script."""
    app = qtw.QApplication(sys.argv)
    widget = ColonyParametersWidget()
    _add_get_value_button(widget=widget)
    window = _wrap_in_window(widget=widget)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    from clovars.gui.gui_utils import _add_get_value_button, _wrap_in_window
    test_loop()
