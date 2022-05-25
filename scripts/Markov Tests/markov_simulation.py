from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import seaborn as sns

sns.set()


def f(t: float) -> float:
    """Defines the function f(t)."""
    return stats.norm(loc=25.0, scale=8.0).cdf(t)


def g(t: float) -> float:
    """Defines the function g(t)."""
    return stats.norm(loc=30.0, scale=4.0).cdf(t)


def get_state_name(state_vector: np.ndarray) -> str:
    """Returns the state name, given its vector."""
    return [
        'Migration',
        'Division',
        'Death',
    ][state_vector.argmax()]


def get_state_number(state_vector: np.ndarray) -> int:
    """Returns the state number, given its vector."""
    return [
        1,
        2,
        3,
    ][state_vector.argmax()]


def get_state_prob(state_vector: np.ndarray) -> str:
    """Returns the state probability, given its vector."""
    return state_vector.max()  # noqa


def get_probs(t: float) -> tuple[float, float, float]:
    """Returns the probabilities of each state at time t."""
    f_t = f(t)
    g_t = g(t)
    union = f_t * g_t
    div_prob = f_t - union
    dth_prob = g_t - union
    mig_prob = 1 - (div_prob + dth_prob)
    return mig_prob, div_prob, dth_prob


def main() -> None:
    """Main function of this script."""
    current_state = np.array([
        1.0,  # Mg. state
        0.0,  # Dv. state
        0.0,  # Dth. state
    ])
    dfs = []
    for t in range(100):
        mig_prob, div_prob, dth_prob = get_probs(t=t)
        transition_matrix = np.array([
            [mig_prob, div_prob, dth_prob],  # Mg. row
            [1.0,           0.0,      0.0],  # Dv. row
            [0.0,           0.0,      1.0],  # Dth. row
        ])  # Mg. col | Dv. col | Dth. col
        current_state = current_state @ transition_matrix
        df = pd.DataFrame({
            'timepoint': t,
            'state_name': get_state_name(state_vector=current_state),
            'state_prob': get_state_prob(state_vector=current_state),
            'state_number': get_state_number(state_vector=current_state),
        }, index=[0])
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    fig, (top_ax, mid_ax, bottom_ax) = plt.subplots(nrows=3, sharex=True)  # noqa
    palette = [
        '#F2909F',
        '#9FF290',
        # '#909FF2',
    ]
    # TOP AX
    sns.lineplot(ax=top_ax, data=data, x='timepoint', y='state_number', color='#232323')
    top_ax.set_title('State Transitions')
    top_ax.set_ylabel('State')
    top_ax.set_yticks([1, 2, 3])
    top_ax.set_yticklabels(['Migration', 'Division', 'Death'])
    # MID AX
    sns.lineplot(ax=mid_ax, data=data, x='timepoint', y='state_prob', hue='state_name', palette=palette)
    mid_ax.get_legend().set_title('State')
    mid_ax.set_title('State Probabilities')
    mid_ax.set_ylabel('State Probability')
    mid_ax.set_xlabel('Time Point')
    # BOTTOM AX
    xs = np.arange(len(data))
    fs = [f(x) for x in xs]
    gs = [g(x) for x in xs]
    sns.lineplot(ax=bottom_ax, x=xs, y=fs, color=palette[0], label='$f(x)$')
    sns.lineplot(ax=bottom_ax, x=xs, y=gs, color=palette[1], label='$g(x)$')
    bottom_ax.get_legend().set_title('Function')
    bottom_ax.set_title('Transition Functions')
    bottom_ax.set_ylabel('Function value')
    bottom_ax.set_xlabel('Time Point')
    # FIG
    fig.suptitle('Markov Chain simulation')
    plt.show()


if __name__ == '__main__':
    main()
