import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats
r = requests.get("https://www.dph.illinois.gov/sitefiles/COVIDHistoricalTestResults.json?nocache=5")
county_json= r.text
regions = pd.read_csv('regions.csv')
data = json.loads(county_json)

table = {}
table['date'] = []
table['county'] = []
table['deaths'] = []
table['count'] = []
table['tested'] = []
table['percentage'] = []
table['deaths_per_million'] = []
table['deaths_7day'] = []
table['count_7day'] = []
table['tested_7day'] = []
table['percentage_7day'] = []
table['deaths_per_million_7day'] = []
table['deaths_14day'] = []
table['count_14day'] = []
table['tested_14day'] = []
table['percentage_14day'] = []
table['deaths_per_million_14day'] = []

startdate=datetime.datetime(2020,4,19)
target_zips = ['60301', '60302', '60304']

for date_data in data['historical_county']['values']:
    date = date_data['testDate']
    for county in date_data['values']:
        table['date'].append(date)
        table['county'].append(county['County'])
        table['tested'].append(county['total_tested'])
        table['count'].append(county['confirmed_cases'])
        table['deaths'].append(county['deaths'])
        table['percentage'].append(0)
        table['deaths_per_million'].append(0)
        table['tested_7day'].append(0)
        table['count_7day'].append(0)
        table['deaths_7day'].append(0)
        table['percentage_7day'].append(0)
        table['deaths_per_million_7day'].append(0)
        table['tested_14day'].append(0)
        table['count_14day'].append(0)
        table['deaths_14day'].append(0)
        table['percentage_14day'].append(0)
        table['deaths_per_million_14day'].append(0)

df = pd.DataFrame(table)
df['date'] = pd.to_datetime(df['date'])
df = pd.merge(df,regions,how='inner', on='county')
df = df.groupby(by=['date','region']).sum()
df = df.reset_index()
df2 = df.pivot(index='date', columns='region')

df2['deaths'] = df2['deaths'].diff(periods=1)
df2['count'] = df2['count'].diff(periods=1)
df2['tested'] = df2['tested'].diff(periods=1)
df2['percentage'] = df2['count'] / df2['tested']
df2.dropna(inplace=True)
# Remove outliers and interpolate
df2.loc[abs(stats.zscore(df2['deaths']['Illinois'])) > 3] = np.nan
df2 = df2.interpolate().round()

values = pd.DataFrame(df2)

df2['deaths_7day'] = df2['deaths'].rolling(window=7).mean()
df2['count_7day'] = df2['count'].rolling(window=7).mean()
df2['tested_7day'] = df2['tested'].rolling(window=7).mean()
df2['percentage_7day'] = df2['count_7day'] / df2['tested_7day']
df2['deaths_per_million_7day'] = 1000000 * df2['deaths_7day'] / df2['population']

df2['deaths_14day'] = df2['deaths'].rolling(window=14).mean()
df2['count_14day'] = df2['count'].rolling(window=14).mean()
df2['tested_14day'] = df2['tested'].rolling(window=14).mean()
df2['percentage_14day'] = df2['count_14day'] / df2['tested_14day']
df2['deaths_per_million_14day'] = 1000000 * df2['deaths_14day'] / df2['population']

df2.to_csv('regional_all.csv')

##############################################################################
# Calculate hospitalization stats
##############################################################################
r = requests.get("https://www.dph.illinois.gov/sitefiles/COVIDHospitalRegions.json?nocache=1")
hospitalization_json= r.text

data = json.loads(hospitalization_json)
history = data['HospitalUtilizationResults']

cols = [ 'TotalBeds','TotalOpenBeds','TotalInUseBedsNonCOVID','TotalInUseBedsCOVID','ICUBeds','ICUOpenBeds', 'ICUInUseBedsNonCOVID','ICUInUseBedsCOVID','VentilatorCapacity','VentilatorAvailable','VentilatorInUseNonCOVID','VentilatorInUseCOVID']
table = {}
table['date'] = []
for column in cols:
    table[column] = []
    table[column+'_change'] = []
    table[column+'_change_7day'] = []
    table[column+'_change_14day'] = []
    table[column+'_7day'] = []
    table[column+'_14day'] = []

for day in history:
    table['date'].append(day['reportDate'])
    for column in cols:
        
        table[column].append(day[column])
        table[column+'_change'].append(0)
        table[column+'_change_7day'].append(0)
        table[column+'_change_14day'].append(0)
        table[column+'_7day'].append(0)
        table[column+'_14day'].append(0)

df = pd.DataFrame(table)
df['date'] = pd.to_datetime(df['date'])

for column in cols:
    df[column+'_change'] = df[column].diff(periods=1)


for column in cols:
    df[column+'_7day'] = df[column].rolling(window=7).mean()
    df[column+'_14day'] = df[column].rolling(window=14).mean()
    df[column+'_change_7day'] = df[column+'_change'].rolling(window=7).mean()
    df[column+'_change_14day'] = df[column+'_change'].rolling(window=14).mean()

df.to_csv('state_hospitalization.csv')