import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats


df = pd.read_csv('owid-covid-data.csv')
df['new_cases_7day'] = 0
df['new_tests_7day'] = 0
df['case_positivity_7day'] = 0
df = pd.DataFrame(df[['date', 'location', 'total_cases',
                      'new_cases', 'total_tests', 'new_tests', 'new_cases_7day', 'new_tests_7day', 'case_positivity_7day']])

df2 = df.pivot(index='date', columns='location')
df2['new_cases_7day'] = df2['new_cases'].rolling(window=7).mean()
df2['new_tests_7day'] = df2['new_tests'].rolling(window=7).mean()
df2['case_positivity_7day'] = df2['new_cases_7day'] / df2['new_tests_7day']

print(df)
