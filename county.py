import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientConnectorError
county_data = {}


async def fetch_html(date: str, session: ClientSession, **kwargs) -> tuple:
    url = "https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetCountyHistoricalTestResults?reportDate="+date
    try:
        resp = await session.request(method="GET", url=url, **kwargs)
    except ClientConnectorError as err:
        return (zip, 404)

    try:
        return (date, await resp.json())
    except:
        return (date, 404)


async def make_requests(**kwargs) -> None:
    date = datetime.datetime(2020, 3, 17)

    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        while ((datetime.datetime.now() - date).days >= 0):
            datestr = date.strftime('%-m/%-d/%y')
            tasks.append(
                fetch_html(date=datestr, session=session, **kwargs)
            )
            date = date + datetime.timedelta(days=1)

        results = await asyncio.gather(*tasks)

    for result in results:
        county_data[result[0]] = result[1]

asyncio.run(make_requests())


def get_regional_breakdown(region_file):
    regions = pd.read_csv(region_file)

    table = {}
    table['date'] = []
    table['county'] = []
    table['deaths'] = []
    table['count'] = []
    table['tested'] = []
    table['percentage'] = []
    table['deaths_per_million'] = []
    table['count_per_million'] = []
    table['deaths_7day'] = []
    table['count_7day'] = []
    table['tested_7day'] = []
    table['percentage_7day'] = []
    table['deaths_per_million_7day'] = []
    table['count_per_million_7day'] = []
    table['deaths_14day'] = []
    table['count_14day'] = []
    table['tested_14day'] = []
    table['percentage_14day'] = []
    table['deaths_per_million_14day'] = []
    table['count_per_million_14day'] = []
    date = datetime.datetime(2020, 3, 17)
    while ((datetime.datetime.now() - date).days >= 0):
        datestr = date.strftime('%-m/%-d/%y')
        data = county_data[datestr]
        if (data == 404):
            date = date + datetime.timedelta(days=1)

            continue
        # pd_date = pd.to_datetime(date)
        print(datestr)
        # if ((pd_date - datetime.datetime(2020, 3, 1)).days < 0):
        #     new_date = datetime.datetime(2021, pd_date.month, pd_date.day)
        #     date = new_date.strftime('%-m/%-d/%Y')
        #     print('BAD '+str(date))
        if (datestr=='4/11/20' or datestr=="4/12/20" or datestr=="10/11/20"):
            date = date + datetime.timedelta(days=1)
            continue
        for county in data['characteristics_by_county']:
            table['date'].append(date)
            table['county'].append(county['CountyName'])
            table['tested'].append(county['tested'])
            table['count'].append(county['confirmed_cases'])
            table['deaths'].append(county['deaths'])
            table['percentage'].append(0)
            table['deaths_per_million'].append(0)
            table['count_per_million'].append(0)
            table['tested_7day'].append(0)
            table['count_7day'].append(0)
            table['deaths_7day'].append(0)
            table['percentage_7day'].append(0)
            table['deaths_per_million_7day'].append(0)
            table['count_per_million_7day'].append(0)
            table['tested_14day'].append(0)
            table['count_14day'].append(0)
            table['deaths_14day'].append(0)
            table['percentage_14day'].append(0)
            table['deaths_per_million_14day'].append(0)
            table['count_per_million_14day'].append(0)
        

        date = date + datetime.timedelta(days=1)

    df = pd.DataFrame(table)
    df['date'] = pd.to_datetime(df['date'])

    df = pd.merge(df, regions, how='inner', on='county')
    df = df.groupby(by=['date', 'region']).sum()
    df = df.reset_index()
    df2 = df.pivot(index='date', columns='region')

    df2['deaths'] = df2['deaths'].diff(periods=1)
    df2['count'] = df2['count'].diff(periods=1)
    df2['tested'] = df2['tested'].diff(periods=1)
    df2.dropna(inplace=True)
    # Remove outliers and interpolate
    #df2.loc[abs(stats.zscore(df2['deaths']['Illinois'])) > 8] = np.nan
    #df2 = df2.interpolate().round()
    #df2.loc[abs(stats.zscore(df2['count']['Illinois'])) > 8] = np.nan
    #df2 = df2.interpolate().round()
    #df2.loc[abs(stats.zscore(df2['tested']['Illinois'])) > 8] = np.nan
    df2 = df2.interpolate().round()
    df2['percentage'] = df2['count'] / df2['tested']
    df2['deaths_per_million'] = 1000000 * df2['deaths'] / df2['population']
    df2['count_per_million'] = 1000000 * df2['count'] / df2['population']

    df2['deaths_7day'] = df2['deaths'].rolling(window=7).mean()
    df2['count_7day'] = df2['count'].rolling(window=7).mean()
    df2['tested_7day'] = df2['tested'].rolling(window=7).mean()
    df2['percentage_7day'] = df2['count_7day'] / df2['tested_7day']
    df2['deaths_per_million_7day'] = 1000000 * \
        df2['deaths_7day'] / df2['population']
    df2['count_per_million_7day'] = 1000000 * \
        df2['count_7day'] / df2['population']

    df2['deaths_14day'] = df2['deaths'].rolling(window=14).mean()
    df2['count_14day'] = df2['count'].rolling(window=14).mean()
    df2['tested_14day'] = df2['tested'].rolling(window=14).mean()
    df2['percentage_14day'] = df2['count_14day'] / df2['tested_14day']
    df2['deaths_per_million_14day'] = 1000000 * \
        df2['deaths_14day'] / df2['population']
    df2['count_per_million_14day'] = 1000000 * \
        df2['count_14day'] / df2['population']
    return df2


get_regional_breakdown('regions.csv').to_csv('regional_all.csv')
get_regional_breakdown('regions_north_south.csv').to_csv(
    'regional_north_south.csv')
state = get_regional_breakdown('regions_state.csv')
state.to_csv('state_all.csv')
state = pd.DataFrame({'positives': state['count_7day']['Illinois'], 'deaths': state['deaths_7day']['Illinois'],
                      'tested': state['tested_7day']['Illinois'], 'percent': state['percentage_7day']['Illinois']})
lastweek = state.tail(8)
lastweek['datestr'] = lastweek.index.strftime('%Y-%m-%d')
lastweek = lastweek.reset_index().set_index('datestr')
lastweek.drop(columns='date', inplace=True)
compare = lastweek.iloc[[0, 7]].transpose()
compare['diff'] = compare.iloc[:, 1] - compare.iloc[:, 0]
compare['change_pct'] = 100 * compare.iloc[:, 2] / compare.iloc[:, 0]
compare.to_csv('illinois_7day_summary.csv')
##############################################################################
# Calculate hospitalization stats
##############################################################################
r = requests.get(
    "https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetHospitalizationResults")
hospitalization_json = r.text

data = json.loads(hospitalization_json)
history = data['HospitalUtilizationResults']

cols = ['TotalBeds', 'TotalOpenBeds', 'TotalInUseBedsNonCOVID', 'TotalInUseBedsCOVID', 'ICUBeds', 'ICUOpenBeds', 'ICUInUseBedsNonCOVID',
        'ICUInUseBedsCOVID', 'VentilatorCapacity', 'VentilatorAvailable', 'VentilatorInUseNonCOVID', 'VentilatorInUseCOVID']
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
    table['date'].append(day['ReportDate'])
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
df = df.set_index('date')
df = df[~df.index.duplicated(keep='first')]
df.to_csv('state_hospitalization.csv')
