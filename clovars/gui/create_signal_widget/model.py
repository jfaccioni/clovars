from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

import numpy as np
import pandas as pd
from PySide6 import QtCore as qtc, QtWidgets as qtw


class SignalModel(qtc.QAbstractTableModel):
    """Model containing a signal's Data."""
    dataPrinted = qtc.Signal(int)

    def __init__(
            self,
            name: str,
            parameters: list[Param],
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalModel instance."""
        super().__init__(parent=parent)
        self.name = name
        self._data = pd.DataFrame({
            'active': False,
            'name': [p.name for p in parameters],
            'value': [p.value for p in parameters],
        })
        self._limits = pd.DataFrame({
            'name': [p.name for p in parameters],
            'min': [p.minimum for p in parameters],
            'max': [p.maximum for p in parameters],
            'step': [p.step for p in parameters],
        })

    def __str__(self) -> str:
        """Returns a string representation of the SignalModel."""
        return (
            '- SignalModel -' + '\n'
            f' {self._data} ' + '\n'
            '---------------'
        )

    def flags(
            self,
            index: qtc.QModelIndex,
    ) -> int:
        """Returns the model's flags - this is used by Qt when deciding if the model can be edited, etc."""
        return (
                qtc.Qt.ItemIsSelectable |  # noqa
                qtc.Qt.ItemIsEnabled |
                qtc.Qt.ItemIsEditable |
                qtc.Qt.ItemIsUserCheckable
        )

    def rowCount(
            self,
            parent: qtw.QWidget = None,
    ) -> int:
        """Returns the number of rows in the model's data."""
        return self._data.shape[0]

    def columnCount(
            self,
            parent: qtw.QWidget = None,
    ) -> int:
        """Returns the number of columns in the model's data."""
        return self._data.shape[1]

    def data(
            self,
            index: qtc.QModelIndex,
            role: int = ...,
    ) -> Any:
        """Returns the model's data, for a given index and role."""
        data = self._data.iat[index.row(), index.column()]
        if role == qtc.Qt.DisplayRole:  # Display the data as a string
            return str(data)
        elif role == qtc.Qt.EditRole:  # Return the data as its proper data type for editing in an appropriate widget
            return from_numpy_dtype(data=data)

    def setData(
            self,
            index: qtc.QModelIndex,
            value: Any,
            role: int = ...,
    ) -> bool:
        """Edits the data on the Model, returning True if the operation was successful."""
        if role == qtc.Qt.EditRole:
            self._data.iat[index.row(), index.column()] = value
            return True
        else:  # Data should not be modified if the role isn't edit
            return False

    def headerData(
            self,
            section: int,
            orientation: qtc.Qt.Orientation,
            role: int = ...,
    ) -> Any:
        """Returns the header data for a given axis (orientation) and position (section)."""
        if role == qtc.Qt.DisplayRole and orientation == qtc.Qt.Horizontal:  # Display the column headers
            return str(self._data.columns[section])

    @qtc.Property(int, int, )
    def printData(
            self,
    ) -> None:
        """Prints the current data selected in the Model."""
        print(self._data)


def from_numpy_dtype(data: Any) -> Any:
    """Converts the data from a numpy dtype to a native Python type."""
    if isinstance(data, np.bool_):
        return bool(data)
    elif isinstance(data, np.int_):
        return int(data)
    elif isinstance(data, np.float_):
        return float(data)
    else:
        return data  # data is not a common numpy type


@dataclass
class Param:
    name: str
    value: float
    minimum: float
    maximum: float
    step: float


INITIAL_VALUE = Param(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05)
PERIOD = Param(name='Period', value=3600.0, minimum=1.0, maximum=1_000_000.0, step=300)
NOISE = Param(name='Noise', value=0.2, minimum=0.0, maximum=1.0, step=0.05)
MEAN = Param(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05)
STD = Param(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05)
K = Param(name='K', value=0.01, minimum=0.0, maximum=100.0, step=0.05)


class ModelManager(qtc.QObject):
    def __init__(
            self,
            parent: qtc.QObject = None
    ):
        super().__init__(parent=parent)
        self.sinusoidal = SignalModel('Sinusoidal', [INITIAL_VALUE, PERIOD])
        self.stochastic = SignalModel('Stochastic', [INITIAL_VALUE, NOISE])
        self.stochSin = SignalModel('StochSin', [INITIAL_VALUE, PERIOD, NOISE])
        self.gaussian = SignalModel('Gaussian', [INITIAL_VALUE, MEAN, STD])
        self.EMGaussian = SignalModel('EMGaussian', [INITIAL_VALUE, MEAN, STD, K])
        self.constant = SignalModel('Constant', [INITIAL_VALUE])

    def __iter__(self) -> Iterator:
        """Returns an iterator over all models."""
        return iter(self.models)

    @property
    def models(self) -> list[SignalModel]:
        """Returns the models."""
        return [self.sinusoidal, self.stochastic, self.stochSin, self.gaussian, self.EMGaussian, self.constant]

    @property
    def names(self) -> list[str]:
        """Return the names of the models."""
        return [model.name for model in self]


def main() -> None:
    """Main function of this script."""
    for model_name, model in MODELS.items():
        print(model_name)
        print(model)


if __name__ == '__main__':
    main()
