import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import multivariate_normal

sns.set()

SETTINGS = {
    'mother_d1_memory': 0.56,
    'mother_d2_memory': 0.98,
    'sister_memory': 0.15,
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
    m_mean, d1_mean, d2_mean = 0.0, 0.0, 0.0
    m_std, d1_std, d2_std = 5.0, 5.0, 5.0
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
        mother = np.random.normal(loc=0.0, scale=5.0)
        mean_vector = np.array([
            [d1_mean],
            [d2_mean]
        ]) + np.array([
            [m_d1_covar],
            [m_d2_covar]
        ]) * (m_mean - m_mean) / m_var
        fluctuation = multivariate_normal.rvs(mean=mean_vector.ravel(), cov=covariance_matrix)
        sister1 = fluctuation[0]
        sister2 = fluctuation[1]
        df = pd.DataFrame({
            'Mother': mother,
            'Sister1': sister1+50,
            'Sister2': sister2+50,
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
