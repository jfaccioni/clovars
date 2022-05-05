from __future__ import annotations

import os
import sys
from typing import Any

from PySide6 import QtCore as qtc, QtGui as qtg, QtQml as qtqml

from gui._deprecated.create_signal_widget.param_model import ParamModel


class CellSignalModel(qtc.QAbstractListModel):
    """A list Model containing a CellSignal's data (ParamModel instances)."""
    nameChanged = qtc.Signal(str)
    paramModelRole = qtc.Qt.UserRole + 1
    paramNameRole = qtc.Qt.UserRole + 2
    paramValueRole = qtc.Qt.UserRole + 3
    paramMinRole = qtc.Qt.UserRole + 4
    paramMaxRole = qtc.Qt.UserRole + 5
    paramStepRole = qtc.Qt.UserRole + 6

    def __init__(
            self,
            name: str = 'CellSignal',
            params: list[ParamModel] = None,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalModel instance."""
        super().__init__(parent=parent)
        self._name = name
        self._params = params or []

    def as_dict(self) -> dict[str, Any]:
        params = {'Name': self._name}
        for param in self._params:
            params.update(param.as_dict())
        return params

    @qtc.Slot()
    def print(self) -> None:
        """Print the current CellSignalModel to the stdout."""
        print(self.as_dict())

    @qtc.Property(str, notify=nameChanged)
    def name(self) -> str:
        """Returns the CellSignalModel's name."""
        return self._name

    @name.setter
    def name(
            self,
            new_name: str,
    ) -> None:
        """Sets the CellSignalModel's name."""
        if new_name != self._name:
            self._name = new_name
            self.nameChanged.emit(new_name)

    def flags(
            self,
            index: qtc.QModelIndex | qtc.QPersistentModelIndex,
    ) -> qtc.Qt.ItemFlags:
        return (
                qtc.Qt.ItemIsEditable |
                qtc.Qt.ItemIsEnabled
        )

    def headerData(
            self,
            section: int = 0,
            orientation: qtc.Qt.Orientation = qtc.Qt.Vertical,
            role: int = ...,
    ) -> Any:
        return self._name

    def rowCount(
            self,
            parent: qtc.QModelIndex | qtc.QPersistentModelIndex = ...,
    ) -> int:
        """Returns the number of rows (ParamModels) in the CellSignalModel."""
        return len(self._params)

    def roleNames(self) -> dict[int, qtc.QByteArray | bytes]:
        return {
            CellSignalModel.paramModelRole: b'paramModel',
            CellSignalModel.paramNameRole: b'paramName',
            CellSignalModel.paramValueRole: b'paramValue',
            CellSignalModel.paramMinRole: b'paramMin',
            CellSignalModel.paramMaxRole: b'paramMax',
            CellSignalModel.paramStepRole: b'paramStep',
        }

    def data(
            self,
            index: qtc.QModelIndex | qtc.QPersistentModelIndex,
            role: int = ...,
    ) -> Any:
        param_model = self._get_param_model(index=index)
        if role == self.paramModelRole:
            return param_model
        elif role == self.paramNameRole:
            return param_model.name
        elif role == self.paramValueRole:
            return param_model.value
        elif role == self.paramMinRole:
            return param_model.minimum
        elif role == self.paramMaxRole:
            return param_model.maximum
        elif role == self.paramStepRole:
            return param_model.step

    def setData(
            self,
            index: qtc.QModelIndex | qtc.QPersistentModelIndex,
            value: Any,
            role: int = ...,
    ) -> bool:
        param_model = self._get_param_model(index=index)
        if role == self.paramValue:
            param_model.value = value
            return True
        return False

    def _get_param_model(
            self,
            index: qtc.QModelIndex | qtc.QPersistentModelIndex,
    ) -> ParamModel:
        """Returns the ParamModel, given a QModelIndex."""
        i = index.row()
        return self._params[i]


def mainloop(qml_path: str) -> None:
    """Creates a simple CellSignalModel attached to a CellSignalView and displays it."""
    app = qtg.QGuiApplication(sys.argv)
    engine = qtqml.QQmlApplicationEngine()
    params = [
        ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
        ParamModel(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05),
        ParamModel(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05),
    ]
    cell_signal_model = CellSignalModel(name='Gaussian', params=params)
    engine.rootContext().setContextProperty("cellSignalModel", cell_signal_model)
    engine.quit.connect(app.quit)  # noqa
    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == '__main__':
    mainloop(qml_path=os.path.join('../..', 'controls', 'CellSignalViewWindow.qml'))
