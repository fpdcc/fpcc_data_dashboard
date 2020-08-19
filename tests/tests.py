import pytest
import pandas as pd
import datatest as dt
from numbers import Number

@pytest.fixture(scope='module')
@dt.working_directory(__file__)
def df():
    return pd.read_csv('data.csv')

@pytest.mark.mandatory
def test_columns(df):
    dt.validate(
        df.columns,
        {'Id','Category','Sub-Category','FPCC Zone','Project Description','Other','Funded','Priority','New Amenity','Rollover CD','Bond','Grant','2020 New CD Funds','Total 2020 Funds','2021','2022','2023','2024','Total 2021-2024'},
    )


def test_rating(df):
    dt.validate.superset(
        df['Category'],
        {'building improvements', 'capital outlays', 'land improvements', 'planning'},
    )


def test_year(df):
    dt.validate(df['Total 2020 Funds'], Number)


def test_runtime(df):
    dt.validate(df['2021'], Number)
