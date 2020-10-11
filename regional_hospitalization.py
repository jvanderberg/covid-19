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

r = requests.get("https://www.dph.illinois.gov/sitefiles/COVID19/ResurgenceMetrics.json?nocache=1")
hospitalization_json= r.text


data = json.loads(hospitalization_json)
print(data.keys())

last_update = data['lastUpdatedDate']
last_update_date = datetime.datetime(last_update['year'], last_update['month'], last_update['day'])
table = {}

table['date'] = []
table['region'] = []
table['testPositivity'] = []
table['hospitalAvailability'] = []
table['surge'] = []
table['icu'] = []
table['cliAdmissions'] = []
for row in data['TestPositivity']:
    table['date'].append(row['reportDate'])
    table['region'].append(row['regionID'])
    table['testPositivity'].append(row['testPositivityRollingAvg'])
df_pos = pd.DataFrame({"date":table['date'], "region": table['region'],"testPositivity": table['testPositivity']})
df_pos = df_pos.set_index(['date', 'region'])
table = {}
table['date'] = []
table['region'] = []
table['testPositivity'] = []
table['hospitalAvailability'] = []
table['surge'] = []
table['icu'] = []
table['cliAdmissions'] = []

for row in data['HospitalAvailability']:
    table['date'].append(row['reportDate'])
    table['region'].append(row['regionID'])
    table['surge'].append(row['AverageMedSurgAvailPct'])
    table['icu'].append(row['AverageICUAvailPct'])
df_icu_surge = pd.DataFrame({"date":table['date'], "region": table['region'],"surge": table['surge'], "icu": table['icu']})
df_icu_surge = df_icu_surge.set_index(['date', 'region'])
table['date'] = []
table['region'] = []
table['testPositivity'] = []
table['hospitalAvailability'] = []
table['surge'] = []
table['icu'] = []
table['cliAdmissions'] = []

for row in data['CLIAdmissions']:
    table['date'].append(row['reportDate'])
    table['region'].append(row['regionID'])
    table['cliAdmissions'].append(row['CLIAdmissionsRA'])
df_cli_admissions = pd.DataFrame({"date":table['date'], "region": table['region'],"cliAdmissions": table['cliAdmissions']})
df_cli_admissions = df_cli_admissions.set_index(['date', 'region'])

df = df_pos.join(df_icu_surge).join(df_cli_admissions)
df = df.drop_duplicates()
df = df.reset_index()
df = df.pivot(index='date',columns='region')
df.to_csv('regional_hospitalization.csv')