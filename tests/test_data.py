from src.data import get_data, new_cases, smooth_cases
import pandas as pd


def test_get_data():
    data = get_data()

    assert isinstance(data, pd.DataFrame)


def test_new_cases():
    data = get_data()
    cases = new_cases(data)

    assert isinstance(cases, pd.DataFrame)
    assert len(cases.columns) == 1
    assert cases.dtypes["cases"] == int
    assert cases.index.nunique() == len(cases)


def test_smooth_cases():
    data = get_data()
    cases = new_cases(data)
    processed = smooth_cases(cases)

    assert isinstance(processed, tuple)
    assert len(processed) == 2

    original = processed[0]
    smoothed = processed[1]

    assert isinstance(original, pd.DataFrame)
    assert isinstance(smoothed, pd.DataFrame)
    assert original.shape == smoothed.shape
    assert len(cases) != len(smoothed)
