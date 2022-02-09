import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

url = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv"


def get_data(url: str = url) -> pd.DataFrame:
    """
    Get data from url

    url: url to csv
    """
    return pd.read_csv(url, sep=";", parse_dates=["Date_of_publication"])[
        ["Date_of_publication", "Total_reported"]
    ]


def get_data_better(url: str = url):
    data = (
        pd.read_csv(url, sep=";", parse_dates=["Date_of_publication"])
        .clean_names()
        .drop(
            columns=[
                "date_of_report",
                "municipality_code",
                "municipality_name",
                "security_region_code",
                "security_region_name",
                "municipal_health_service",
                "roaz_region",
                "version",
            ]
        )
        .rename(
            columns={
                "date_of_publication": "date",
                "province": "provincie",
                "total_reported": "cases",
            }
        )
    )
    return data


def new_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes data to get new case counts

    df: pandas DataFrame
    """

    # Only get total cases based on date of publication
    df = df.groupby(df["Date_of_publication"].dt.date).sum().reset_index()

    # Rename columns
    df.columns = ["date", "cases"]

    # Set date as index
    df = df.set_index("date")

    return df


def smooth_cases(df: pd.DataFrame, window: int = 7, cutoff: int = 25) -> pd.DataFrame:
    """
    Smooth new case data

    df: pandas DataFrame
    window: rolling windown used for smoothing
    cuttoff: get start when new cases > cutoff
    """

    # Calculate smoohted new cases
    smoothed = (
        df.rolling(7, win_type="gaussian", min_periods=1, center=True)
        .mean(std=2)
        .round()
    )

    # Get start index when new cases > cutoff
    idx_start = np.searchsorted(smoothed.values.flatten(), cutoff)

    # Filter smoothed and original based on cutoff
    smoothed = smoothed.iloc[idx_start:]
    original = df.loc[smoothed.index]

    return original, smoothed
