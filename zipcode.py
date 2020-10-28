import json
import datetime
import pandas as pd
import numpy as np
import requests
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientConnectorError

age_groups = ['Unknown', '<20', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']

zip_demographics = {}
async def fetch_html(zip:str, session: ClientSession, **kwargs) -> tuple:
    url = "https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetZipDemographics?zipCode="+zip
    try:
        resp = await session.request(method="GET", url=url, **kwargs)
    except ClientConnectorError as err:
        return (zip, 404)
    return (zip, await resp.json())

async def make_requests(zips, **kwargs) -> None:
    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        for zip_data in zips:
            tasks.append(
                fetch_html(zip=zip_data['zip'], session=session, **kwargs)
            )
        results = await asyncio.gather(*tasks)

    for result in results:
        zip_demographics[result[0]] = result[1] 

#fetch the latest file and save it
r = requests.get("https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetZip")
zip_json= r.text
data = json.loads(zip_json)
file_date = datetime.datetime(data['lastUpdatedDate']['year'], data['lastUpdatedDate']['month'], data['lastUpdatedDate']['day'])

asyncio.run(make_requests(data['zip_values']))
for zip_data in data['zip_values']:
    print(zip_data['zip'])
    groups = []
    group = {}
    zip_age_groups = {}
    for zip_age_group in zip_demographics[zip_data['zip']]['age']:
        zip_age_groups[zip_age_group['age_group'].strip()] = zip_age_group

    for age_group in age_groups:
        try:
            # Get the existing group if available, zero reports are excluded
            group = zip_age_groups[age_group]
            # Rebuild the object because they have spaces appended to group names
            group = {"age_group": age_group, "count": group['count'], "tested":  group['tested'] }
        except:
            # Fake a record to match the old file format
            group = {"age_group": age_group, "count": 0, "tested": 0 }

        groups.append(group)
 
    zip_data['demographics'] = zip_demographics[zip_data['zip']]
    zip_data['demographics']['age'] = groups

# file_date = datetime.datetime.now()
file_name = file_date.strftime("%m-%d") + ".json"
f = open(file_name, "w")
json.dump(data,f)
f.close()

startdate=datetime.datetime(2020,4,19,0,0,0,0)
target_zips = ['60301', '60302', '60304']
#target_zips = ['60402']
population = pd.DataFrame({'zip':target_zips, 'population':[ 2536.00, 32048, 17641]}).set_index('zip')
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


for age_group in age_groups:
    table[age_group+' tested'] = []
    table[age_group+' count'] = []
    table[age_group+' percentage'] = []

for age_group in age_groups:
    table[age_group+' tested_14day'] = []
    table[age_group+' count_14day'] = []
    table[age_group+' percentage_14day'] = []

age_index = 0
last_good_file = None

while ((datetime.datetime.now() - date).days >= 0):
    file = date.strftime("%m-%d") + ".json"
    print(file)

    try:
        open(file)
        last_good_file = file
        bad_file = False
    except:
        print('No such file: '+ file)
        bad_file = True

    if (bad_file == False or last_good_file):
        data = json.load(open(last_good_file))
        try:
            fileDate = datetime.datetime(data['LastUpdateDate']['year'], data['LastUpdateDate']['month'], data['LastUpdateDate']['day'])
        except:
            fileDate = datetime.datetime(data['lastUpdatedDate']['year'], data['lastUpdatedDate']['month'], data['lastUpdatedDate']['day'])

        strdate= date.strftime("%m-%d")
        for zip_data in data['zip_values']:
            if (bad_file):
                table['zip'].append( zip_data['zip'])
                table['date'].append(date)
                table['count'].append(np.NaN)
                table['7daypos100k'].append(np.NaN)
                table['tested'].append(np.NaN)
                table['percentage'].append(0)
                table['count_14day'].append(np.NaN)
                table['tested_14day'].append(np.NaN)
                table['percentage_14day'].append(0)
                table['7daypos100k_14day'].append(np.NaN)
                for age_group in age_groups:
                    table[age_group + " count"].append(np.NaN)
                    table[age_group + " tested"].append(np.NaN)
                    table[age_group + " percentage"] = 0
                    table[age_group + " count_14day"].append(np.NaN)
                    table[age_group + " tested_14day"].append(np.NaN)
                    table[age_group + " percentage_14day"] = 0

            else:
                table['zip'].append( zip_data['zip'])
                table['date'].append(date)
                table['count'].append(zip_data['confirmed_cases'])
                table['tested'].append(zip_data['total_tested'])
                table['7daypos100k'].append(np.NaN)

                table['percentage'].append(0)
                table['count_14day'].append(np.NaN)
                table['tested_14day'].append(np.NaN)
                table['percentage_14day'].append(0)
                table['7daypos100k_14day'].append(np.NaN)
                demographics_exist = False
                try:
                    zip_data['demographics']['age']
                    demographics_exist = True
                except:
                    demographics_exist = False
                if (demographics_exist):
                    age_index = 0
                    for age_group in zip_data['demographics']['age']:
                        table[age_groups[age_index] + " count"].append(age_group['count'])
                        table[age_groups[age_index] + " tested"].append(age_group['tested'])
                        table[age_groups[age_index] + " percentage"] = 0
                        table[age_groups[age_index] + " count_14day"].append(np.NaN)
                        table[age_groups[age_index] + " tested_14day"].append(np.NaN)
                        table[age_groups[age_index] + " percentage_14day"] = 0
                        age_index = age_index + 1
                else:
                    for age_group in age_groups:
                        table[age_group + " count"].append(np.NaN)
                        table[age_group + " tested"].append(np.NaN)
                        table[age_group + " percentage"] = 0
                        table[age_group + " count_14day"].append(np.NaN)
                        table[age_group + " tested_14day"].append(np.NaN)
                        table[age_group + " percentage_14day"] = 0


    
    date = date + datetime.timedelta(days= 1)

df = pd.DataFrame(table)
df = df[df['zip'].isin(target_zips)]
df['date'] = pd.to_datetime(df['date'])
df = df.join(population, on='zip')
df2 = df.pivot(index='date',columns='zip')
df2 = df2.interpolate()
diff = pd.DataFrame(df2)
diff['count'] = diff['count'].diff(periods=1)
diff['tested'] = diff['tested'].diff(periods=1)
diff['count'] = diff['count'].round()
diff['tested'] = diff['tested'].round()


for age_group in age_groups:
    diff[age_group+' count']  = diff[age_group+' count'].diff(periods=1)
    diff[age_group+' tested']  = diff[age_group+' tested'].diff(periods=1)

diff['7daypos100k'] = 100000 * diff['count'].rolling(window=7).sum() / diff['population']
diff['percentage'] = diff['count'] / diff['tested']
for age_group in age_groups:
    diff[age_group+' percentage']  = diff[age_group+' count'] / diff[age_group+' tested']


diff['count_14day'] = diff['count'].rolling(window=14).mean()
diff['tested_14day'] = diff['tested'].rolling(window=14).mean()
diff['percentage_14day'] = diff['count_14day'] / diff['tested_14day']
diff['7daypos100k_14day'] = diff['7daypos100k'].rolling(window=14).mean()

for age_group in age_groups:
    diff[age_group+' percentage']  = diff[age_group+' count'] / diff[age_group+' tested']
    diff[age_group+' count_14day'] = diff['count'].rolling(window=14).mean()
    diff[age_group+' tested_14day'] = diff['tested'].rolling(window=14).mean()
    diff[age_group+' percentage_14day']  = diff[age_group+' count_14day'] / diff[age_group+' tested_14day']

diff.to_csv('zip_detail_all.csv')

dftotals = diff.transpose()
dftotals = dftotals.sum(level=0)
dftotals = dftotals.transpose()

dftotals['percentage'] = dftotals['count'] / dftotals['tested']
for age_group in age_groups:
    dftotals[age_group+' percentage']  = dftotals[age_group+' count'] / dftotals[age_group+' tested']

dftotals['count_14day'] = dftotals['count'].rolling(window=14).mean()
dftotals['tested_14day'] = dftotals['tested'].rolling(window=14).mean()
dftotals['percentage_14day'] = dftotals['count_14day'] / dftotals['tested_14day']
dftotals['7daypos100k'] = 100000 * dftotals['count'].rolling(window=7).sum() / dftotals['population']
dftotals['7daypos100k_14day'] = dftotals['7daypos100k'].rolling(window=14).mean()

for age_group in age_groups:
    dftotals[age_group+' percentage']  = dftotals[age_group+' count'] / dftotals[age_group+' tested']
    dftotals[age_group+' count_14day'] = dftotals[age_group+' count'].rolling(window=14).mean()
    dftotals[age_group+' tested_14day'] = dftotals[age_group+' tested'].rolling(window=14).mean()
    dftotals[age_group+' percentage_14day']  = dftotals[age_group+' count_14day'] / dftotals[age_group+' tested_14day']

dftotals.to_csv('zip_rollup_all.csv')

population = pd.read_csv('cook_zipcodes.csv').set_index('zip')

keys = ['zip', 'date', 'count', 'tested']
subset =  {key: table[key] for key in keys }
subset['cases_per_million_14day'] = subset['count']
df = pd.DataFrame(subset)
# df = df[df['zip'].isin(population.index)]
df['zip'] = df['zip'].astype('int')
df['date'] = pd.to_datetime(df['date'])
df = df.pivot(index='date',columns='zip').interpolate()

count = df['count'].reset_index().melt(id_vars=('date'), value_name='count').set_index(keys=['date','zip']).join(population, on='zip', how='inner')
tested = df['tested'].reset_index().melt(id_vars=('date'), value_name='tested').set_index(keys=['date','zip']).join(population, on='zip', how='inner')
out = count.join(tested, rsuffix='_')
df = pd.DataFrame( out, columns=['zip','city','count','tested','population'])
keys = [ '7daypos100k', 'percentage', 'count_14day', 'tested_14day', 'percentage_14day', '7daypos100k_14day', 'cases_per_million_14day']
for key in keys:
    df[key] = 0
df = df[df['population'] > 0]
df = df.groupby(by=['city', 'date']).sum()
df = df.reset_index()
df2 = df.pivot(index='date',columns='city')
diff = pd.DataFrame(df2)
diff['count'] = diff['count'].diff(periods=1)
diff['tested'] = diff['tested'].diff(periods=1)
diff['count'] = diff['count'].round()
diff['tested'] = diff['tested'].round()


diff['7daypos100k'] = 100000 * diff['count'].rolling(window=7).sum() / diff['population']
diff['percentage'] = diff['count'] / diff['tested']


diff['count_14day'] = diff['count'].rolling(window=14).mean()
diff['cases_per_million_14day'] = 1000000*diff['count_14day'] / diff['population'] 
diff['tested_14day'] = diff['tested'].rolling(window=14).mean()
diff['percentage_14day'] = diff['count_14day'] / diff['tested_14day']
diff['7daypos100k_14day'] = diff['7daypos100k'].rolling(window=14).mean()

diff.to_csv('zip_city_all.csv')





