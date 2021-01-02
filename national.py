import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats

df = pd.read_csv("https://api.covidtracking.com/v1/us/daily.csv",
                 parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
smooth = df['hospitalizedIncrease'].rolling(window=14, center=True).mean()
df.loc[df['hospitalizedIncrease'] > 5000, 'hospitalizedIncrease'] = smooth
rolling = df.rolling(window=7).mean()

export = df.join(rolling, rsuffix="_7day")
export['positivity_7day'] = 100*export['positiveIncrease_7day'] / \
    export['totalTestResultsIncrease_7day']
export.to_csv('us_daily.csv')
lastweek = export[['positivity_7day', 'deathIncrease_7day', 'hospitalizedCurrently_7day',
                   'positiveIncrease_7day', 'totalTestResultsIncrease_7day']].tail(8)
lastweek['datestr'] = lastweek.index.strftime('%Y-%m-%d')
lastweek = lastweek.reset_index().set_index('datestr')
lastweek.drop(columns='date', inplace=True)
compare = lastweek.iloc[[0, 7]].transpose()
compare['diff'] = compare.iloc[:, 1] - compare.iloc[:, 0]
compare['change_pct'] = 100 * compare.iloc[:, 2] / compare.iloc[:, 0]
compare.to_csv('us_daily_7day_summary.csv')
