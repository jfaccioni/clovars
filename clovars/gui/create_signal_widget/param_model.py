from __future__ import annotations

import os
import sys
from functools import partial
from typing import Any

from PySide6 import QtCore as qtc, QtGui as qtg, QtQml as qtqml


class ParamModel(qtc.QObject):
    """Model containing a parameter, including its value and min/max/step."""
    nameChanged = qtc.Signal(str)
    valueChanged = qtc.Signal(float)
    minimumChanged = qtc.Signal(float)
    maximumChanged = qtc.Signal(float)
    stepChanged = qtc.Signal(float)
    activeStateChanged = qtc.Signal(bool)

    def __init__(
            self,
            name: str = 'Param',
            value: float = 5.0,
            minimum: float = 0.0,
            maximum: float = 10.0,
            step: float = 1.0,
            is_active: bool = False,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a ParamModel instance."""
        super().__init__(parent=parent)
        self._name = name
        self._value = value
        self._minimum = minimum
        self._maximum = maximum
        self._step = step
        self._active = is_active

    def as_dict(self) -> dict[str, float]:
        return {self._name: self._value if self._active else None}

    @qtc.Slot()
    def print(self) -> None:
        """Print the current ParamModel to the stdout."""
        print(self.as_dict())

    @qtc.Property(str, notify=nameChanged)
    def name(self) -> str:
        """Returns the ParamModel's name."""
        return self._name

    @name.setter
    def name(
            self,
            new_name: str,
    ) -> None:
        """Sets the ParamModel's name."""
        if new_name != self._name:
            self._name = new_name
            self.nameChanged.emit(new_name)

    @qtc.Property(float, notify=valueChanged)
    def value(self) -> float:
        """Returns the ParamModel's value."""
        return self._value

    @value.setter
    def value(
            self,
            new_value: float,
    ) -> None:
        """Sets the ParamModel's value."""
        if new_value != self._value:
            self._value = new_value
            self.valueChanged.emit(new_value)

    @qtc.Property(float, notify=minimumChanged)
    def minimum(self) -> float:
        """Returns the ParamModel's minimum."""
        return self._minimum

    @minimum.setter
    def minimum(
            self,
            new_minimum: float,
    ) -> None:
        """Sets the ParamModel's minimum."""
        if new_minimum != self._minimum:
            self._minimum = new_minimum
            self.minimumChanged.emit(new_minimum)

    @qtc.Property(float, notify=maximumChanged)
    def maximum(self) -> float:
        """Returns the ParamModel's maximum."""
        return self._maximum

    @maximum.setter
    def maximum(
            self,
            new_maximum: float,
    ) -> None:
        """Sets the ParamModel's maximum."""
        if new_maximum != self._maximum:
            self._maximum = new_maximum
            self.maximumChanged.emit(new_maximum)

    @qtc.Property(float, notify=stepChanged)
    def step(self) -> float:
        """Returns the ParamModel's step."""
        return self._step

    @step.setter
    def step(
            self,
            new_step: float,
    ) -> None:
        """Sets the ParamModel's step."""
        if new_step != self._step:
            self._step = new_step
            self.stepChanged.emit(new_step)

    @qtc.Property(bool, notify=activeStateChanged)
    def activeState(self) -> bool:
        """Returns the ParamModel's active state."""
        return self._active

    @activeState.setter
    def activeState(
            self,
            new_active_state: bool,
    ) -> None:
        """Sets the ParamModel's active state."""
        if new_active_state != self._active:
            self._active = new_active_state
            self.activeStateChanged.emit(new_active_state)


def mainloop(qml_path: str) -> None:
    """Creates a simple ParamModel attached to a ParamViewWindow and displays it."""
    app = qtg.QGuiApplication(sys.argv)
    param_model = ParamModel()

    engine = qtqml.QQmlApplicationEngine()

    engine.rootContext().setContextProperty('model', param_model)
    engine.quit.connect(app.quit)  # noqa

    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == '__main__':
    QML_PATH = os.path.join('..', 'controls', 'ParamViewWindow.qml')
    mainloop(qml_path=QML_PATH)
