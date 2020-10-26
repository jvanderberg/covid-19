import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats

df = pd.read_csv("https://api.covidtracking.com/v1/us/daily.csv",parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
rolling = df.rolling(window=7).mean()

export = df.join(rolling, rsuffix="_7day")
export['positivity_7day'] = 100*export['positiveIncrease_7day']/export['totalTestResultsIncrease_7day']
export.to_csv('us_daily.csv')


