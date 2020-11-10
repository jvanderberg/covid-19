import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib
import datetime


start = datetime.datetime(2020, 6, 11)
daysback = (datetime.datetime.now() - start).days

pos = {}
hosp = {}

pos['date'] = []
pos['region'] = []
pos['testPositivity'] = []
pos['totalTests'] = []
pos['positiveTests'] = []
pos['cliAdmissions'] = []

hosp['date'] = []
hosp['region'] = []
hosp['beds'] = []
hosp['icu'] = []

regions = ['', 'North', 'North-Central', 'West-Central', 'Metro East', 'Southern',
           'East-Central', 'South Suburban', 'West Suburban', 'North Suburban', 'Suburban Cook', 'Chicago']
for region in range(1, 12):

    r = requests.get(
        "https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetResurgenceData?regionID="+str(region)+"&daysIncluded="+str(daysback))
    hospitalization_json = r.text
    data = json.loads(hospitalization_json)
    for row in data['TestPositivity']:
        if row['regionID'] == 14:
            continue
        pos['date'].append(datetime.datetime.strptime(
            row['reportDate'][0:10], "%Y-%m-%d"))
        pos['region'].append(regions[row['regionID']])
        pos['positiveTests'].append(row['positiveTests'])
        pos['totalTests'].append(row['totalTests'])
        pos['testPositivity'].append(row['testPositivityRollingAvg'])

    for row in data["CLIAdmissions"]:
        if row['regionID'] == 14:
            continue
        pos['cliAdmissions'].append(row['CLIAdmissionsRA'])

    for row in data['HospitalAvailability']:
        if row['regionID'] == 14:
            continue
        hosp['date'].append(datetime.datetime.strptime(
            row['reportDate'][0:10], "%Y-%m-%d"))

        hosp['region'].append(regions[row['regionID']])
        hosp['beds'].append(row['AverageMedSurgAvailPct'])
        hosp['icu'].append(row['AverageICUAvailPct'])


last_update = data['lastUpdatedDate']
last_update_date = datetime.datetime(
    last_update['year'], last_update['month'], last_update['day'])

df_pos = pd.DataFrame(
    {"date": pos['date'], "region": pos['region'], "cliAdmissions": pos['cliAdmissions'], "testPositivity": pos['testPositivity'], "positiveTests": pos['positiveTests'], "totalTests": pos['totalTests']})
df_pos = df_pos.set_index(['date', 'region'])
table = {}
df_icu_beds = pd.DataFrame(
    {"date": hosp['date'], "region": hosp['region'], "beds": hosp['beds'], "icu": hosp['icu']})
df_icu_beds = df_icu_beds.set_index(['date', 'region'])
df_pos.to_csv('regional_hospitalization_pos.csv')
df_icu_beds.to_csv('regional_hospitalization_beds.csv')

df = df_icu_beds.join(df_pos, how='outer')
df = df.drop_duplicates()
df = df.reset_index()
df = df.pivot(index='date', columns='region')
df = df[df.index >= start]
df.to_csv('regional_hospitalization.csv')
