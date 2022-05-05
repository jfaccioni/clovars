from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from PySide6 import QtCore as qtc, QtGui as qtg, QtWidgets as qtw


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


class CellSignalModel(qtc.QAbstractTableModel):
    """Class representing the model containing the CellSignal data."""
    stepChanged = qtc.Signal(int)

    def __init__(
            self,
            model_name: str = '',
            model_params: list[Param] = None,
    ) -> None:
        super().__init__()
        self.name = model_name
        self.params = model_params or []
        self._data = pd.DataFrame(
            {
                'Use this parameter?': False,
                'Parameter name': [param.name for param in self.params],
                'Parameter value': [param.value for param in self.params],
            }
        )
        self._limits = [{
            'objectName': param.name,
            'minimum': param.minimum,
            'maximum': param.maximum,
            'singleStep': param.step,
        } for param in self.params]
        self._step = 1

    @qtc.Property(int, notify=stepChanged)
    def step(self) -> int:
        return self._step

    @step.setter
    def step(
            self,
            new_step,
    ) -> None:
        self._step = new_step

    def rowCount(
            self,
            parent: qtw.QWidget = None,
    ) -> int:
        return self._data.shape[0]

    def columnCount(
            self,
            parent: qtw.QWidget = None,
    ) -> int:
        return self._data.shape[1]

    def flags(
            self,
            index: qtc.QModelIndex,
    ) -> int:
        return qtc.Qt.ItemIsSelectable | qtc.Qt.ItemIsEnabled | qtc.Qt.ItemIsEditable | qtc.Qt.ItemIsUserCheckable

    def data(
            self,
            index: qtc.QModelIndex,
            role: int = ...,
    ) -> Any:
        data = self._data.iat[index.row(), index.column()]
        if role == qtc.Qt.DisplayRole:  # must convert to string first
            return str(data)
        elif role == qtc.Qt.EditRole:  # no data conversion
            if isinstance(data, np.bool_):
                return bool(data)
            elif isinstance(data, np.float_):
                return float(data)
            elif isinstance(data, np.int_):
                return int(data)
            return data

    def headerData(
            self,
            section: int,
            orientation: qtc.Qt.Orientation,
            role: int = ...,
    ) -> Any:
        if role == qtc.Qt.DisplayRole and orientation == qtc.Qt.Horizontal:
            return self._data.columns[section]

    def setData(
            self,
            index: qtc.QModelIndex,
            value: Any,
            role: int = ...,
    ) -> bool:
        if role == qtc.Qt.EditRole:
            if not self.checkIndex(index):
                return False
            self._data.iat[index.row(), index.column()] = value
            return True
        return False


MODELS = [
    CellSignalModel('Sinusoidal', [INITIAL_VALUE, PERIOD]),
    CellSignalModel('Stochastic', [INITIAL_VALUE, NOISE]),
    CellSignalModel('Stoch. + Sin.', [INITIAL_VALUE, PERIOD, NOISE]),
    CellSignalModel('Gaussian', [INITIAL_VALUE, MEAN, STD]),
    CellSignalModel('E. M. Gaussian', [INITIAL_VALUE, MEAN, STD, K]),
    CellSignalModel('Constant', [INITIAL_VALUE]),
]

# @dataclass
# class SinusoidalCellSignalModel:
#     name: str = 'Sinusoidal'
#     initial_value: Param = INITIAL_VALUE
#     period: Param = PERIOD
#
#     @property
#     def params(self) -> list[Param]:
#         """docstring"""
#         return [self.initial_value, self.period]
#
#
# @dataclass
# class StochasticCellSignalModel:
#     name: str = 'Stochastic'
#     initial_value: Param = INITIAL_VALUE
#     noise: Param = NOISE
#
#     @property
#     def params(self) -> list[Param]:
#         """docstring"""
#         return [self.initial_value, self.noise]
#
#
# @dataclass
# class StochasticSinusoidalCellSignalModel:
#     name: str = 'Stoch. + Sin.'
#     initial_value: Param = INITIAL_VALUE
#     period: Param = PERIOD
#     noise: Param = NOISE
#
#     @property
#     def params(self) -> list[Param]:
#         """docstring"""
#         return [self.initial_value, self.period, self.noise]
#
#
# @dataclass
# class GaussianCellSignalModel:
#     name: str = 'Gaussian'
#     initial_value: Param = INITIAL_VALUE
#     mean: Param = MEAN
#     std: Param = STD
#
#     @property
#     def params(self) -> list[Param]:
#         """docstring"""
#         return [self.initial_value, self.mean, self.std]
#
#
# @dataclass
# class EMGaussianCellSignalModel:
#     name: str = 'E. M. Gaussian'
#     initial_value: Param = INITIAL_VALUE
#     mean: Param = MEAN
#     std: Param = STD
#     k: Param = K
#
#     @property
#     def params(self) -> list[Param]:
#         """docstring"""
#         return [self.initial_value, self.mean, self.std, self.k]
#
#
# @dataclass
# class ConstantCellSignalModel:
#     name: str = 'Constant'
#     initial_value: Param = INITIAL_VALUE
#
#     @property
#     def params(self) -> list[Param]:
#         """docstring"""
#         return [self.initial_value]
#
#
# class SpinBoxDelegate(qtw.QStyledItemDelegate):
#     def paint(
#             self,
#             painter: qtg.QPainter,
#             option: qtw.QStyleOptionViewItem,
#             index: qtc.QModelIndex,
#     ) -> None:
#         if index.column() != 0:
#             super().paint(painter, option, index)
#         else:
#             checked = True if index.data() == 'True' else False
#             check_box_style_option = qtw.QStyleOptionButton()
#             if checked:
#                 check_box_style_option.state |= qtw.QStyle.State_On
#             else:
#                 check_box_style_option.state |= qtw.QStyle.State_Off
#             check_box_style_option.rect = self.getCheckBoxRect(option)
#             check_box_style_option.state |= qtw.QStyle.State_Enabled
#             qtw.QApplication.style().drawControl(qtw.QStyle.CE_CheckBox, check_box_style_option, painter)
#
#     @staticmethod
#     def getCheckBoxRect(option: qtw.QStyleOptionViewItem) -> qtc.QRect:
#         check_box_style_option = qtw.QStyleOptionButton()
#         check_box_rect = qtw.QApplication.style().subElementRect(
#             qtw.QStyle.SE_CheckBoxIndicator,
#             check_box_style_option,
#             None
#         )
#         check_box_point = qtc.QPoint(
#             option.rect.x() +
#             option.rect.width() / 2 -
#             check_box_rect.width() / 2,
#             option.rect.y() +
#             option.rect.height() / 2 -
#             check_box_rect.height() / 2
#         )
#         return qtc.QRect(check_box_point, check_box_rect.size())
#
#     def editorEvent(
#             self,
#             event,
#             model,
#             option,
#             index,
#     ):
#         if index.column() != 0:
#             return super().editorEvent(event, model, option, index)
#         else:
#             # Do not change the checkbox-state
#             if event.type() == qtc.QEvent.MouseButtonPress:
#                 return False
#             if event.type() == qtc.QEvent.MouseButtonRelease or event.type() == qtc.QEvent.MouseButtonDblClick:
#                 if event.button() != qtc.Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
#                     return False
#                 if event.type() == qtc.QEvent.MouseButtonDblClick:
#                     return True
#             elif event.type() == qtc.QEvent.KeyPress:
#                 if event.key() != qtc.Qt.Key_Space and event.key() != qtc.Qt.Key_Select:
#                     return False
#             else:
#                 return True
#             # Change the checkbox-state
#             mock_editor = qtw.QCheckBox()
#             mock_editor.setEnabled(index.data(qtc.Qt.EditRole))
#             self.setModelData(mock_editor, model, index)
#             return True
#
#     def createEditor(
#             self,
#             parent: qtw.QWidget,
#             option: qtw.QStyleOptionViewItem,
#             index: qtc.QModelIndex,
#     ) -> qtw.QCheckBox | qtw.QDoubleSpinBox | None:
#         if index.column() == 2:  # value column
#             params = index.model()._limits[index.row()]  # noqa
#             editor = qtw.QDoubleSpinBox(parent=parent, **params)  # noqa
#             editor.setFrame(False)
#         else:
#             return
#         return editor
#
#     def setEditorData(
#             self,
#             editor: qtw.QCheckBox | qtw.QDoubleSpinBox,
#             index: qtc.QModelIndex,
#     ) -> None:
#         data = index.data(role=qtc.Qt.EditRole)  # noqa
#         if index.column() == 0:  # bool column
#             editor.setChecked(data)
#         elif index.column() == 2:  # value column
#             editor.setValue(data)
#
#     def setModelData(
#             self,
#             editor: qtw.QCheckBox | qtw.QDoubleSpinBox,
#             model: qtc.QAbstractItemModel,
#             index: qtc.QModelIndex,
#     ) -> None:
#         if index.column() == 0:  # bool column
#             value = editor.isChecked()
#         if index.column() == 2:  # value column
#             editor.interpretText()
#             value = editor.value()
#         model.setData(index=index, value=value, role=qtc.Qt.EditRole)  # noqa
#
#     def updateEditorGeometry(
#             self,
#             editor: qtw.QCheckBox | qtw.QDoubleSpinBox,
#             option: qtw.QStyleOptionViewItem,
#             index: qtc.QModelIndex,
#     ) -> None:
#         if index.column() in [0, 2]:  # bool or value columns
#             editor.setGeometry(option.rect)  # noqa
#
#
# def main() -> None:
#     for model_name, model_params in MODELS.items():
#         model = CellSignalModel(model_name=model_name, model_params=model_params)
#         print(model.data)
#
#     a = qtw.QApplication(sys.argv)
#     tableView = qtw.QTableView()
#     myModel = CellSignalModel(model_name='Gaussian', model_params=MODELS['Gaussian'])
#     tableView.setModel(myModel)
#     delegate = SpinBoxDelegate()
#     tableView.setItemDelegate(delegate)
#     tableView.show()
#     a.exec()
#
#
# if __name__ == '__main__':
#     main()
