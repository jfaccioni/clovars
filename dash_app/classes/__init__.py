from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Param:
    name: str
    value: float
    min_: float
    max_: float
    step: float

    def to_dict(self) -> dict:
        return {
            'value': self.value,
            'min': self.min_,
            'max': self.max_,
            'step': self.step,
        }


@dataclass
class Signal:
    name: str
    params: list[Param]
