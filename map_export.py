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
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import shapely.geometry as sgeom

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader

matplotlib.rcParams['text.color'] = '#555555'
matplotlib.rcParams['axes.labelcolor'] = '#555555'
matplotlib.rcParams['xtick.color'] = '#555555'
matplotlib.rcParams['ytick.color'] = '#555555'

# states = ['CO','WY','NE','KS','OK','NM','AZ','UT']
# statenames = ['Colorado', 'Wyoming', 'Nebraska', 'Kansas', 'Oklahoma', 'New Mexico', 'Arizona','Utah']
# statefips= [8, 56, 31, 20, 40, 35, 4, 49]
settings = {'CO': {'name': 'Colorado Area', 'states': ['CO', 'WY', 'NE', 'KS', 'OK', 'NM', 'AZ', 'UT'], 'title_font': 30, 'datex': -102, 'datey': 30, 'figsize': (10, 9), 'dpi': 400, 'extent': [-115, -94, 30, 45]},
            'IL': {'name': 'Midwest', 'states': ['OH', 'MN', 'IL', 'KY', 'IN', 'MO', 'IA', 'MI', 'WI'], 'title_font': 24, 'datex': -96, 'datey': 34, 'figsize': (7, 8), 'dpi': 400, 'extent': [-98, -82, 35, 50]},
            'US': {'name': 'US', 'states': ['AK', 'AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'], 'title_font': 24, 'datex': -120, 'datey': 22, 'figsize': (12, 7), 'dpi': 400, 'extent': [-122, -73.5, 22, 50]}}


all_state_fips = pd.read_csv('state_fips.csv')
population = pd.read_csv('time_series_covid19_deaths_US.csv')
population = pd.DataFrame(
    {'county': population['Admin2'], 'statename': population['Province_State'], 'population': population['Population']})
population = population.set_index(['county', 'statename'])


def get_all_county_data(setting, fips, stat):
    df = pd.read_csv('time_series_covid19_'+stat+'_US.csv')

    df = df[df['Province_State'].isin(fips['statename'])]

    df['county'] = df['Admin2']
    df['statename'] = df['Province_State']

    date = datetime.datetime(2020, 4, 1)
    cols = []
    while ((datetime.datetime.now() - date).days >= 1):
        try:
            col = date.strftime('%-m/%-d/%y')
            cols.append(col)
        except:
            print('No date '+col)
        date = date + datetime.timedelta(days=1)
    cols.append('statename')
    cols.append('county')
    cols.append('FIPS')
    df2 = pd.DataFrame(df[cols])
    df2 = df2.set_index(['county', 'statename', 'FIPS'])
    df2 = df2.fillna(value=0)
    df2 = df2.transpose()
    df2 = df2.diff(periods=1)
    df2 = df2.rolling(window=14).mean()
    df2 = df2.dropna()
    max = df2.max().max()
    print('Max value for stat: '+stat+' = '+str(max))
    stats = df2.max().describe()
    print(stats)
    df2 = df2.transpose()
    df = df2.join(population)
    return df, stats


setting = settings['US']
state_fips = all_state_fips[all_state_fips['state'].isin(setting['states'])]

current_date = datetime.datetime.today()

counties_confirmed, cases_stats = get_all_county_data(
    setting, state_fips, 'confirmed')
counties_deaths, death_stats = get_all_county_data(
    setting, state_fips, 'deaths')
counties_confirmed = counties_confirmed.reset_index().round(decimals=2)
counties_death = counties_deaths.reset_index().round(decimals=2)
cases = {}
keys = ['statename', 'county', 'FIPS', 'population']
for col in counties_confirmed:
    if (col in keys):
        cases[col] = counties_confirmed[col].values.tolist()
    else:
        cases[col+"cases"] = counties_confirmed[col].values.tolist()
        cases[col+"deaths"] = counties_death[col].values.tolist()

f = open('county_combined.json', 'w')
str = json.dumps(cases, separators=(',', ':')).replace('NaN', 'null')
f.write(str)
