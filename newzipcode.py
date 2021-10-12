import json
import datetime
import pandas as pd
import numpy as np
import requests
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientConnectorError

age_groups = ['Unknown', '<20', '20-29', '30-39',
              '40-49', '50-59', '60-69', '70-79', '80+']

zip_data = {}

#https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetZip?format=csv&reportDate=12/01/2020
async def fetch_html(date: str, session: ClientSession, **kwargs) -> tuple:
    url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetZip?reportDate="+date
    try:
        resp = await session.request(method="GET", url=url, **kwargs)
    except ClientConnectorError as err:
        return (zip, 404)

    try:
        return (date, await resp.json())
    except:
        return (date, 404)


async def make_requests(**kwargs) -> None:
    date = datetime.datetime(2020, 4, 19)

    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        while ((datetime.datetime.now() - date).days >= 0):
            datestr = date.strftime('%-m/%-d/%Y')
            tasks.append(
                fetch_html(date=datestr, session=session, **kwargs)
            )
            date = date + datetime.timedelta(days=1)

        results = await asyncio.gather(*tasks)

    for result in results:
        zip_data[result[0]] = result[1]

asyncio.run(make_requests())


startdate = datetime.datetime(2020, 4, 19, 0, 0, 0, 0)
target_zips = ['60301', '60302', '60304']
#target_zips = ['60402']
population = pd.DataFrame({'zip': target_zips, 'population': [
                          2536.00, 32048, 17641]}).set_index('zip')
#population = pd.DataFrame({'zip':target_zips, 'population':[ 63448]}).set_index('zip')
date = startdate
df = pd.DataFrame()
bad_file = False
table = {}
table['zip'] = []
table['date'] = []
table['count'] = []
table['tested'] = []
table['7daypos100k'] = []
table['percentage'] = []
table['count_14day'] = []
table['tested_14day'] = []
table['percentage_14day'] = []
table['7daypos100k_14day'] = []


while ((datetime.datetime.now() - date).days >= 0):
    #file = date.strftime("%m-%d") + ".json"
    datestr = date.strftime("%-m/%-d/%Y")

    data = zip_data[datestr]

    for zip in data:

            table['zip'].append(zip['zip'])
            table['date'].append(date)
            table['count'].append(zip['confirmed_cases'])
            table['tested'].append(zip['total_tested'])
            table['7daypos100k'].append(np.NaN)

            table['percentage'].append(0)
            table['count_14day'].append(np.NaN)
            table['tested_14day'].append(np.NaN)
            table['percentage_14day'].append(0)
            table['7daypos100k_14day'].append(np.NaN)

    date = date + datetime.timedelta(days=1)

df = pd.DataFrame(table)
df = df[df['zip'].isin(target_zips)]
df['date'] = pd.to_datetime(df['date'])
df = df.join(population, on='zip')
df2 = df.pivot(index='date', columns='zip')
df2 = df2.interpolate()
diff = pd.DataFrame(df2)
diff.to_csv("temp.csv")
diff['count'] = diff['count'].diff(periods=1)
diff['tested'] = diff['tested'].diff(periods=1)
diff['count'] = diff['count'].round()
diff['tested'] = diff['tested'].round()
diff.to_csv("temp2.csv")


diff['7daypos100k'] = 100000 * \
    diff['count'].rolling(window=7).sum() / diff['population']
diff['percentage'] = diff['count'] / diff['tested']


diff['count_14day'] = diff['count'].rolling(window=14).mean()
diff['tested_14day'] = diff['tested'].rolling(window=14).mean()
diff['percentage_14day'] = diff['count_14day'] / diff['tested_14day']
diff['7daypos100k_14day'] = diff['7daypos100k'].rolling(window=14).mean()

diff.to_csv('zip_detail_all.csv')

dftotals = diff.transpose()
dftotals = dftotals.sum(level=0)
dftotals = dftotals.transpose()

dftotals['percentage'] = dftotals['count'] / dftotals['tested']

dftotals['count_14day'] = dftotals['count'].rolling(window=14).mean()
dftotals['tested_14day'] = dftotals['tested'].rolling(window=14).mean()
dftotals['percentage_14day'] = dftotals['count_14day'] / \
    dftotals['tested_14day']
dftotals['7daypos100k'] = 100000 * \
    dftotals['count'].rolling(window=7).sum() / dftotals['population']
dftotals['7daypos100k_14day'] = dftotals['7daypos100k'].rolling(
    window=14).mean()


dftotals.to_csv('zip_rollup_all.csv')

population = pd.read_csv('cook_zipcodes.csv').set_index('zip')

keys = ['zip', 'date', 'count', 'tested']
subset = {key: table[key] for key in keys}
subset['cases_per_million_14day'] = subset['count']
df = pd.DataFrame(subset)
# df = df[df['zip'].isin(population.index)]
df['zip'] = df['zip'].astype('int')
df['date'] = pd.to_datetime(df['date'])
df = df.pivot(index='date', columns='zip').interpolate()

count = df['count'].reset_index().melt(id_vars=('date'), value_name='count').set_index(
    keys=['date', 'zip']).join(population, on='zip', how='inner')
tested = df['tested'].reset_index().melt(id_vars=('date'), value_name='tested').set_index(
    keys=['date', 'zip']).join(population, on='zip', how='inner')
out = count.join(tested, rsuffix='_')
df = pd.DataFrame(out, columns=['zip', 'city',
                                'count', 'tested', 'population'])
keys = ['7daypos100k', 'percentage', 'count_14day', 'tested_14day',
        'percentage_14day', '7daypos100k_14day', 'cases_per_million_14day']
for key in keys:
    df[key] = 0
df = df[df['population'] > 0]
df = df.groupby(by=['city', 'date']).sum()
df = df.reset_index()
df2 = df.pivot(index='date', columns='city')
diff = pd.DataFrame(df2)
diff['count'] = diff['count'].diff(periods=1)
diff['tested'] = diff['tested'].diff(periods=1)
diff['count'] = diff['count'].round()
diff['tested'] = diff['tested'].round()


diff['7daypos100k'] = 100000 * \
    diff['count'].rolling(window=7).sum() / diff['population']
diff['percentage'] = diff['count'] / diff['tested']


diff['count_14day'] = diff['count'].rolling(window=14).mean()
diff['cases_per_million_14day'] = 1000000 * \
    diff['count_14day'] / diff['population']
diff['tested_14day'] = diff['tested'].rolling(window=14).mean()
diff['percentage_14day'] = diff['count_14day'] / diff['tested_14day']
diff['7daypos100k_14day'] = diff['7daypos100k'].rolling(window=14).mean()

diff.to_csv('zip_city_all.csv')

diff[diff['population'] > 30000]['cases_per_million_14day'].tail(1).transpose().dropna().to_csv(
    'zip_city_cases_per_million_latest.csv')
diff[diff['population'] > 30000]['percentage_14day'].tail(1).transpose().dropna().to_csv(
    'zip_city_percentage_latest.csv')
diff['count_14day'].tail(1).transpose().to_csv('zip_city_cases_latest.csv')
