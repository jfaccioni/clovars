from __future__ import annotations

import pprint

from PySide6 import QtCore as qtc

from clovars.gui.create_signal_widget.param_model import ParamModel
from clovars.gui.create_signal_widget.signal_model import SignalModel


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
