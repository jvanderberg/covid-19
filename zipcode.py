import json
import datetime
import pandas as pd
import numpy as np
import requests

#fetch the latest file and save it
r = requests.get("https://www.dph.illinois.gov/sitefiles/COVIDZip.json?nocache=1")
zip_json= r.text
data = json.loads(zip_json)
file_date = datetime.datetime(data['LastUpdateDate']['year'], data['LastUpdateDate']['month'], data['LastUpdateDate']['day'])
file_name = file_date.strftime("%m-%d") + ".json"
f = open(file_name, "w")
f.write(r.text)
f.close()

startdate=datetime.datetime(2020,4,19,0,0,0,0)
target_zips = ['60301', '60302', '60304']

date = startdate
df = pd.DataFrame()
bad_file = False
table = {}
table['zip'] = []
table['date'] = []
table['count'] = []
table['tested'] = []
table['percentage'] = []
table['count_14day'] = []
table['tested_14day'] = []
table['percentage_14day'] = []
age_groups = ['Unknown', '<20', '20-39', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']

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
        fileDate = datetime.datetime(data['LastUpdateDate']['year'], data['LastUpdateDate']['month'], data['LastUpdateDate']['day'])
        strdate= date.strftime("%m-%d")
        for zip_data in data['zip_values']:
          #  df2 = pd.DataFrame()
            if (bad_file):
                table['zip'].append( zip_data['zip'])
                table['date'].append(date)
                table['count'].append(np.NaN)
                table['tested'].append(np.NaN)
                table['percentage'].append(0)
                table['count_14day'].append(np.NaN)
                table['tested_14day'].append(np.NaN)
                table['percentage_14day'].append(0)
                age_index = 0
                for age_group in zip_data['demographics']['age']:
                    table[age_groups[age_index] + " count"].append(np.NaN)
                    table[age_groups[age_index] + " tested"].append(np.NaN)
                    table[age_groups[age_index] + " percentage"] = 0
                    table[age_groups[age_index] + " count_14day"].append(np.NaN)
                    table[age_groups[age_index] + " tested_14day"].append(np.NaN)
                    table[age_groups[age_index] + " percentage_14day"] = 0
                    age_index = age_index + 1

            else:
                table['zip'].append( zip_data['zip'])
                table['date'].append(date)
                table['count'].append(zip_data['confirmed_cases'])
                table['tested'].append(zip_data['total_tested'])
                table['percentage'].append(0)
                table['count_14day'].append(np.NaN)
                table['tested_14day'].append(np.NaN)
                table['percentage_14day'].append(0)
                age_index = 0
                for age_group in zip_data['demographics']['age']:
                    table[age_groups[age_index] + " count"].append(age_group['count'])
                    table[age_groups[age_index] + " tested"].append(age_group['tested'])
                    table[age_groups[age_index] + " percentage"] = 0
                    table[age_groups[age_index] + " count_14day"].append(np.NaN)
                    table[age_groups[age_index] + " tested_14day"].append(np.NaN)
                    table[age_groups[age_index] + " percentage_14day"] = 0
                    age_index = age_index + 1


    
    date = date + datetime.timedelta(days= 1)

df = pd.DataFrame(table)
df = df[df['zip'].isin(target_zips)]
df['date'] = pd.to_datetime(df['date'])

df2 = df.pivot(index='date',columns='zip')
df2 = df2.interpolate().round()

diff = df2.diff(periods=1)
diff['percentage'] = diff['count'] / diff['tested']
for age_group in age_groups:
    diff[age_group+' percentage']  = diff[age_group+' count'] / diff[age_group+' tested']


diff['count_14day'] = diff['count'].rolling(window=14).mean()
diff['tested_14day'] = diff['tested'].rolling(window=14).mean()
diff['percentage_14day'] = diff['count_14day'] / diff['tested_14day']
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

for age_group in age_groups:
    dftotals[age_group+' percentage']  = dftotals[age_group+' count'] / dftotals[age_group+' tested']
    dftotals[age_group+' count_14day'] = dftotals['count'].rolling(window=14).mean()
    dftotals[age_group+' tested_14day'] = dftotals['tested'].rolling(window=14).mean()
    dftotals[age_group+' percentage_14day']  = dftotals[age_group+' count_14day'] / dftotals[age_group+' tested_14day']

dftotals.to_csv('zip_rollup_all.csv')



