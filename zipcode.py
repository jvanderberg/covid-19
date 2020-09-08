import json
import datetime
import pandas as pd
import numpy as np
startdate=datetime.datetime(2020,4,19)
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
age_groups = ['Unknown', '<20', '20-39', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']

for age_group in age_groups:
    table[age_group+' tested'] = []
    table[age_group+' count'] = []
    table[age_group+' percentage'] = []

age_index = 0
last_good_file = None

while (date <= datetime.datetime.now()):
    file = date.strftime("%m-%d") + ".json"
    print(file)
    try:
        open(file)
        last_good_file = file
        bad_file = False
    except:
        print('No such file'+ file)
        bad_file = True

    if (bad_file == False or last_good_file):
        data = json.load(open(last_good_file))
        fileDate = datetime.datetime(data['LastUpdateDate']['year'], data['LastUpdateDate']['month'], data['LastUpdateDate']['day'])
        strdate= date.strftime("%m-%d")
        for zip_data in data['zip_values']:
          #  df2 = pd.DataFrame()
            if (bad_file):
                table['zip'].append( zip_data['zip'])
                table['date'].append(strdate)
                table['count'].append(np.NaN)
                table['tested'].append(np.NaN)
                table['percentage'].append(0)
                age_index = 0
                for age_group in zip_data['demographics']['age']:
                    table[age_groups[age_index] + " count"].append(np.NaN)
                    table[age_groups[age_index] + " tested"].append(np.NaN)
                    table[age_groups[age_index] + " percentage"] = 0
                    age_index = age_index + 1

            else:
                table['zip'].append( zip_data['zip'])
                table['date'].append(strdate)
                table['count'].append(zip_data['confirmed_cases'])
                table['tested'].append(zip_data['total_tested'])
                table['percentage'].append(0)
                age_index = 0
                for age_group in zip_data['demographics']['age']:
                    table[age_groups[age_index] + " count"].append(age_group['count'])
                    table[age_groups[age_index] + " tested"].append(age_group['tested'])
                    table[age_groups[age_index] + " percentage"] = 0
                    age_index = age_index + 1


    
    date = date + datetime.timedelta(days= 1)

df = pd.DataFrame(table)
df = df[df['zip'].isin(target_zips)]
df2 = df.pivot(index='date',columns='zip')
df2 = df2.interpolate().round()

diff = df2.diff(periods=1)
diff['percentage'] = diff['count'] / diff['tested']
for age_group in age_groups:
    diff[age_group+' percentage']  = diff[age_group+' count'] / diff[age_group+' tested']

diff.to_csv('zip_counts.csv')
dftotals = diff.transpose()
dftotals = dftotals.sum(level=0)
dftotals = dftotals.transpose()
dftotals.to_csv('totals_counts.csv')
dftotals['percentage'] = dftotals['count'] / dftotals['tested']
for age_group in age_groups:
    dftotals[age_group+' percentage']  = dftotals[age_group+' count'] / dftotals[age_group+' tested']

dftotals.to_csv('totals_counts.csv')

total_rolling = dftotals.rolling(window=14).mean()
total_rolling['percentage'] = total_rolling['count'] / total_rolling['tested']
for age_group in age_groups:
    total_rolling[age_group+' percentage']  = total_rolling[age_group+' count'] / total_rolling[age_group+' tested']

total_rolling.to_csv('totals_14day.csv')

roll = diff.rolling(window=14).mean()
roll['percentage'] = roll['count'] / roll['tested']
for age_group in age_groups:
    roll[age_group+' percentage']  = roll[age_group+' count'] /roll[age_group+' tested']

roll.to_csv('zip_14day.csv')

