from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import exponnorm

curr_dir = Path(__file__).parent

xs = np.linspace(0, 144, 1_000)
for death_mean in [35.09, 45.09, 55.09, 65.09, 75.09]:
    fig, ax = plt.subplots(figsize=(16, 8))
    ys_div = exponnorm(loc=12.72, scale=8.50, K=2.87).pdf(xs)
    ys_dth = exponnorm(loc=death_mean, scale=23.75, K=2.93).pdf(xs)
    ax.plot(xs, ys_div, label='TMZ Division Curve', linewidth=5)
    ax.plot(xs, ys_dth, label='TMZ Death Curve', linewidth=5) 
    ax.legend()
    fig.suptitle(f'TMZ curves (Death mean = {death_mean}')
    plt.savefig(curr_dir / f'TMZ_{death_mean}mean.png')
    plt.close(fig=fig)
