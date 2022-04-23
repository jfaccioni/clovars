from __future__ import annotations

import pprint
from typing import Any

from PySide6 import QtCore as qtc


class ParamModel(qtc.QObject):
    """Model containing a parameter, including its value and min/max/step."""
    nameChanged = qtc.Signal(str)
    valueChanged = qtc.Signal(float)
    minimumChanged = qtc.Signal(float)
    maximumChanged = qtc.Signal(float)
    stepChanged = qtc.Signal(float)

    def __init__(
            self,
            name: str,
            value: float,
            minimum: float,
            maximum: float,
            step: float,
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a ParamModel instance."""
        super().__init__(parent=parent)
        self._name = name
        self._value = value
        self._minimum = minimum
        self._maximum = maximum
        self._step = step

    def as_dict(self) -> dict[str, float]:
        return {self._name: self._value}

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


class SignalModel(qtc.QObject):
    """Model containing a signal's Data."""
    nameChanged = qtc.Signal(str)
    paramsChanged = qtc.Signal(list)

    def __init__(
            self,
            name: str,
            parameters: list[ParamModel],
            parent: qtc.QObject = None,
    ) -> None:
        """Initializes a SignalModel instance."""
        super().__init__(parent=parent)
        self._name = name
        self._params = parameters

    @qtc.Property(str, notify=nameChanged)
    def name(self) -> str:
        """Returns the SignalModel's name."""
        return self._name

    @name.setter
    def name(
            self,
            new_name: str,
    ) -> None:
        """Sets the SignalModel's name."""
        if new_name != self._name:
            self._name = new_name
            self.nameChanged.emit(new_name)

    @qtc.Property(list, notify=paramsChanged)
    def params(self) -> list[ParamModel]:
        """Returns the list of ParamModel instances."""
        return self._params

    @params.setter
    def params(
            self,
            new_params: list[ParamModel] = None,
    ) -> None:
        """Sets the list of ParamModel instances."""
        if new_params is not None:
            self._params = new_params
            self.paramsChanged.emit(new_params)


class SignalModelManager(qtc.QObject):
    """Manager object that has a reference to all SignalModels and ParamModels"""
    signalNamesChanged = qtc.Signal(list)
    signalModelsChanged = qtc.Signal(list)
    signalIndexChanged = qtc.Signal(int)

    initial_value = ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05)
    period = ParamModel(name='Period', value=3600.0, minimum=1.0, maximum=1_000_000.0, step=300)
    noise = ParamModel(name='Noise', value=0.2, minimum=0.0, maximum=1.0, step=0.05)
    mean = ParamModel(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05)
    std = ParamModel(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05)
    k = ParamModel(name='K', value=0.01, minimum=0.0, maximum=100.0, step=0.05)

    def __init__(
            self,
            parent: qtc.QObject = None,
    ):
        super().__init__(parent=parent)
        self.signals = [
            SignalModel('Sinusoidal', [self.initial_value, self.period]),
            SignalModel('Stochastic', [self.initial_value, self.noise]),
            SignalModel('StochSin', [self.initial_value, self.period, self.noise]),
            SignalModel('Gaussian', [self.initial_value, self.mean, self.std]),
            SignalModel('EMGaussian', [self.initial_value, self.mean, self.std, self.k]),
            SignalModel('Constant', [self.initial_value]),
        ]
        self.signal_names = [signal.name for signal in self.signals]
        self.signal_index = 0

    @qtc.Property(list, notify=signalModelsChanged)
    def signalModels(self) -> list[SignalModel]:
        return self.signals

    @signalModels.setter
    def signalsModels(
            self,
            new_signals: list[SignalModel]
    ) -> None:
        self.signals = new_signals

    @qtc.Property(list, notify=signalNamesChanged)
    def signalNames(self) -> list[str]:
        return self.signal_names

    @signalNames.setter
    def signalNames(
            self,
            new_signal_names: list[str]
    ) -> None:
        self.signal_names = new_signal_names

    @qtc.Property(int, notify=signalIndexChanged)
    def signalIndex(self) -> int:
        return self.signal_index

    @signalIndex.setter
    def signalIndex(
            self,
            new_signal_index: int
    ) -> None:
        self.signal_index = new_signal_index

    @qtc.Slot()
    def displayModel(self) -> None:
        current_signal = self.signals[self.signal_index]
        data = {'name': current_signal.name}
        for param in current_signal.params:
            data.update(param.as_dict())
        pprint.pprint(data)
