from __future__ import annotations

import numpy as np
from scipy.stats import norm, exponnorm, gamma, lognorm

Numeric = int | float | np.ndarray  # noqa
Curve = type[norm] | type[exponnorm] | type[gamma] | type[lognorm]  # noqa
