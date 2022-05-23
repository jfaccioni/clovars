import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import multivariate_normal, logistic

from clovars.scientific import reflect_around_interval

sns.set()

SETTINGS = {
    'mother_d1_memory': 0.05,
    'mother_d2_memory': 0.05,
    'sister_memory': 0.78,
}


def main(
        mother_d1_memory: float,
        mother_d2_memory: float,
        sister_memory: float,
) -> None:
    """Main function of this script."""
    # SOURCE: https://stats.stackexchange.com/a/437682/325570
    # covariance = np.array([
    #     [1, sister_memory],
    #     [sister_memory, 1],
    # ])
    dfs = []
    m_mean, d1_mean, d2_mean = 0.5, 0.0, 0.0
    m_std, d1_std, d2_std = 1.0, 1.0, 1.0
    m_var, d1_var, d2_var = m_std**2, d1_std**2, d2_std**2
    m_d1_corr = mother_d1_memory
    m_d1_covar = m_d1_corr * (m_std * d1_std)
    m_d2_corr = mother_d2_memory
    m_d2_covar = m_d2_corr * (m_std * d2_std)
    d1_d2_corr = sister_memory
    d1_d2_covar = d1_d2_corr * (d1_std * d2_std)
    # covariance_matrix = (np.array([[d1_var, d1_d2_corr], [d1_d2_corr, d2_var]]) - (  # C_aa
    #         np.array([[m_d1_corr], [m_d2_corr]]) @  # C_ab
    #         np.linalg.inv(np.array([[m_var]])) @  # C_bb-1
    #         np.array([[m_d1_corr, m_d2_corr]])  # C_ba
    # ))
    covariance_matrix = np.array([
        [d1_var,      d1_d2_covar],
        [d1_d2_covar,      d2_var]
    ]) - np.array([
        [m_d1_covar**2,           m_d1_covar * m_d2_covar],
        [m_d2_covar * m_d1_covar,           m_d2_covar**2]
    ]) / m_var
    # Avoid scipy positive-semi-definite warnings (false positives):
    # Source: https://stackoverflow.com/a/41518536/11161432
    if (min_eig := np.min(np.real(np.linalg.eigvals(covariance_matrix)))) < 0:
        covariance_matrix -= 10 * min_eig * np.eye(*covariance_matrix.shape)
    for _ in range(10_000):
        # mother = np.random.uniform(low=0.0, high=1.0)
        # mean_vector = (np.array([[d1_mean], [d2_mean]]) + (      # u_a
        #         np.array([[m_d1_corr], [m_d2_corr]]) @           # C_ab
        #         np.linalg.inv(np.array([[m_var]])) @             # C_bb-1
        #         (mother - np.array([[m_mean]]))                  # (x_b - u_b)
        # ))
        mother = np.random.normal(loc=m_mean, scale=m_std)
        mean_vector = np.array([
            [d1_mean],
            [d2_mean]
        ]) + np.array([
            [m_d1_covar],
            [m_d2_covar]
        ]) * (mother - m_mean) / m_var
        fluctuation = multivariate_normal.rvs(mean=mean_vector.ravel(), cov=covariance_matrix)
        sister1 = fluctuation[0]
        sister2 = fluctuation[1]
        # sister1 = mother + fluctuation[0]
        # sister2 = mother + fluctuation[1]
        # sister1 = logistic.cdf(mother + fluctuation[0] * (1-mother_memory), loc=0.5)
        # sister2 = logistic.cdf(mother + fluctuation[1] * (1-mother_memory), loc=0.5)
        # sister1 = reflect_around_interval(
        #     x=fluctuation[0],
        #     lower_bound=0.0,
        #     upper_bound=1.0,
        # )
        # sister2 = reflect_around_interval(
        #     x=fluctuation[1],
        #     lower_bound=0.0,
        #     upper_bound=1.0,
        # )
        # sister1 = reflect_around_interval(
        #     x=mother + fluctuation[0],
        #     lower_bound=0.0,
        #     upper_bound=1.0,
        # )
        # sister2 = reflect_around_interval(
        #     x=mother + fluctuation[1],
        #     lower_bound=0.0,
        #     upper_bound=1.0,
        # )
        df = pd.DataFrame({
            'Mother': mother,
            'Sister1': sister1,
            'Sister2': sister2,
        }, index=[0])
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    sns.pairplot(data=data, corner=True)
    corr = data.corr()
    with sns.axes_style("white"):
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        _, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(ax=ax, data=corr, mask=mask, square=True, annot=True)
    plt.show(block=True)


if __name__ == '__main__':
    main(
        mother_d1_memory=SETTINGS['mother_d1_memory'],
        mother_d2_memory=SETTINGS['mother_d2_memory'],
        sister_memory=SETTINGS['sister_memory'],
    )
