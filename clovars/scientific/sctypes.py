from __future__ import annotations

from typing import Union

import numpy as np
from scipy.stats import norm, exponnorm, gamma, lognorm

Numeric = Union[int, float, np.ndarray]
Curve = Union[type(norm()), type(exponnorm(K=1)), type(gamma(a=1)), type(lognorm(s=1))]
