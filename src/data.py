import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

url = "https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data/rivm_NL_covid19_national.csv"


def get_data(url: str = url) -> pd.DataFrame:
    """
    Get data from url

    url: url to csv
    """
    return pd.read_csv(url, parse_dates=['Datum'])


def new_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes data to get new case counts

    df: pandas DataFrame
    """

    # Only get total cases
    df = df[df['Type'] == 'Totaal']
    df = df.drop(columns='Type')

    # Rename columns
    df.columns = ['date', 'cases']

    # Set date as index
    df = df.set_index('date')

    # Calculate new cases
    df = df.diff().fillna(0).astype(int)
    return df


def smooth_cases(df: pd.DataFrame, window: int = 7, cutoff: int = 25) -> pd.DataFrame:
    """
    Smooth new case data

    df: pandas DataFrame
    window: rolling windown used for smoothing
    cuttoff: get start when new cases > cutoff
    """

    # Calculate smoohted new cases
    smoothed = (df
                .rolling(7, win_type='gaussian', min_periods=1, center=True)
                .mean(std=2)
                .round())

    # Get start index when new cases > cutoff
    idx_start = np.searchsorted(smoothed.values.flatten(), cutoff)

    # Filter smoothed and original based on cutoff
    smoothed = smoothed.iloc[idx_start:]
    original = df.loc[smoothed.index]

    return original, smoothed
