from typing import List
import pandas as pd
import janitor  # noaq
from src import model
from src.data import get_data_better
from src.model import highest_density_interval

from tqdm import tqdm


cases = get_data_better()

reported = (
    cases.groupby([cases["date"].dt.date, cases["provincie"]])
    .sum()[["cases"]]
    .reset_index()
)

# Replace dace with zero cases with a one
reported.cases = reported.cases.replace({0: 1})

# Get all provinces in the Netherlands
provincies = reported["provincie"].unique()

results: List[pd.DataFrame] = []

for i, provincie in tqdm(enumerate(provincies)):
    # Filter on provincie
    provincies_reported = (
        reported[reported["provincie"] == provincies[i]]
        .reset_index(drop=True)
        .set_index("date")
    )

    # Get smoothed cases
    smoothed = (
        provincies_reported.rolling(7, win_type="gaussian", min_periods=1, center=True)
        .mean(std=2)
        .round()
    )

    # Get posteriors and log_likelihood
    posteriors, log_likelihood = model.get_posteriors(smoothed)

    # Get HDI based on posteriors
    hdi = highest_density_interval(posteriors, p=0.90)

    # Set provincie name in column
    hdi["provincie"] = provincie

    # Append dataframe list
    results.append(hdi)


final = pd.concat(results).reset_index()
final.date = pd.to_datetime(final.date)

# Dataframe
cases_df = (
    cases.groupby([cases.date.dt.date, "provincie"])
    .sum()
    .reset_index()
    .sort_values(["provincie", "date"])
    .reset_index(drop=True)
)

cases_df["most_likely"] = final["most_likely"]
cases_df["low_90"] = final["low_90"]
cases_df["high_90"] = final["high_90"]

nl_df = cases.groupby([cases.date]).sum()  # .reset_index()
smooth_nl = (
    nl_df[["cases"]]
    .rolling(7, win_type="gaussian", min_periods=1, center=True)
    .mean(std=2)
    .round()
)
nl_rt, _ = model.get_posteriors(smooth_nl)
nl_hdi = highest_density_interval(nl_rt, p=0.90).reset_index()

nl = cases_df.groupby(["date"]).mean().reset_index()
nl["provincie"] = "Nederland"

covid = pd.concat([cases_df, nl])
covid.date = pd.to_datetime(covid.date).dt.date
covid = covid.sort_values(["provincie", "date"]).reset_index(drop=True)


covid.to_csv("data/covid.csv", index=False)
