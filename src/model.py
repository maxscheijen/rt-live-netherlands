"""
Model developed by Kevin Systrom
See README for the model
"""
import numpy as np
import pandas as pd
import scipy.stats as stats
from tqdm import tqdm


def get_posteriors(df: pd.DataFrame, sigma: float = 0.25) -> pd.DataFrame:
    """
    Get posteriors

    df: pandas DataFrame
    sigma: amount of noise added from gaussian process
    """

    # Set variables
    rt_max = 12
    rt_range = np.linspace(0, rt_max, rt_max * 100 + 1)
    GAMMA = 1 / 7

    # 1. Calculate lambda
    lam = df[:-1].values * np.exp(GAMMA * (rt_range[:, None].T - 1))

    # 2. Calculate each day's likelihood
    likelihoods = pd.DataFrame(
        data=stats.poisson.pmf(df[1:].values, lam), columns=rt_range, index=df.index[1:]
    ).transpose()

    # 3. Create the Gaussian Matrix
    process_matrix = stats.norm(loc=rt_range, scale=sigma).pdf(rt_range[:, None])

    # 3a. Normalize all rows to sum to 1
    process_matrix /= process_matrix.sum(axis=0)

    # (4) Calculate the initial prior
    # prior0 = sps.gamma(a=4).pdf(r_t_range)
    prior0 = np.ones_like(rt_range) / len(rt_range)
    prior0 /= prior0.sum()

    # Create a DataFrame that will hold our posteriors for each day
    # Insert our prior as the first posterior.
    posteriors = pd.DataFrame(
        index=rt_range, columns=df.index, data={df.index[0]: prior0}
    )

    # Keep track of the sum of the log of the probability of the data for maximum likelihood calculation.
    log_likelihood = 0.0

    # 5. Iteratively apply Bayes' rule
    for previous_day, current_day in zip(df.index[:-1], df.index[1:]):

        # 5a. Calculate the new prior
        current_prior = process_matrix @ posteriors[previous_day]

        # 5b. Calculate the numerator of Bayes' Rule: P(k|R_t)P(R_t)
        numerator = likelihoods[current_day] * current_prior

        # 5c. Calcluate the denominator of Bayes' Rule P(k)
        denominator = np.sum(numerator)

        # Execute full Bayes' Rule
        posteriors[current_day] = numerator / denominator

        # Add to the running sum of log likelihoods
        log_likelihood += np.log(denominator)

    return posteriors, log_likelihood


def highest_density_interval(posteriors: pd.DataFrame, p=0.9) -> pd.DataFrame:
    """
    Get HDI

    posteriors: pandas DataFrame of posteriors
    p: confidence interval
    """

    # If we pass a DataFrame, just call this recursively on the columns
    if isinstance(posteriors, pd.DataFrame):
        return pd.DataFrame(
            [highest_density_interval(posteriors[col], p=p) for col in posteriors],
            index=posteriors.columns,
        )

    cumsum = np.cumsum(posteriors.values)

    # N x N matrix of total probability mass for each low, high
    total_p = cumsum - cumsum[:, None]

    # Return all indices with total_p > p
    lows, highs = (total_p > p).nonzero()

    # Find the smallest range (highest density)
    best = (highs - lows).argmin()

    low = posteriors.index[lows[best]]
    most_likely = posteriors.idxmax(axis=0)
    high = posteriors.index[highs[best]]

    return pd.Series(
        [most_likely, low, high],
        index=["most_likely", f"low_{p*100:.0f}", f"high_{p*100:.0f}"],
    ).round(2)


def bayesian_model(
    df: pd.DataFrame, p=0.90, save_posteriors_df=False, optimize=True
) -> pd.DataFrame:
    """
    Bayesian model that optimzes for the best sigma

    df: pandas DataFrame
    """

    # Sigmas to consider
    sigmas = np.linspace(1 / 20, 1, 20)

    # Initialize dict to hold posteriors and log likelihoods
    result = {}
    result["posteriors"] = []
    result["log_likelihoods"] = []

    # Loop over all sigmas and store posteriors and log likelihoods
    if optimize:
        for sigma in tqdm(sigmas):
            posteriors, log_likelihood = get_posteriors(df=df, sigma=sigma)
            result["posteriors"].append(posteriors)
            result["log_likelihoods"].append(log_likelihood)

        # Total log likelohhods for each sigma
        total_log_likelihoods = np.zeros_like(sigmas)

        # Add log to total
        total_log_likelihoods += result["log_likelihoods"]

        # Get index with max log likelihood total
        max_likelihood_index = total_log_likelihoods.argmax()

        # Get corresponding posteriors
        posteriors = result["posteriors"][max_likelihood_index]

    else:
        posteriors, log_likelihood = get_posteriors(df=df)

    # Get most likely Rt and HDI
    likely_hdi = []
    for p in [0.65, 0.95]:
        likely_hdi.append(highest_density_interval(posteriors, p=p))

    likely_hdi = pd.merge(
        left=likely_hdi[0], right=likely_hdi[1], on=["date", "most_likely"]
    )

    # Save DataFrame with most likely Rt and HDI to CSV
    if save_posteriors_df:
        likely_hdi.to_csv("data/most_likely_rt.csv", index=True)

    return likely_hdi
