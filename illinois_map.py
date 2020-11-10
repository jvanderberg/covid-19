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


def get_regional_breakdown(region_file):
    r = requests.get(
        "https://www.dph.illinois.gov/sitefiles/COVIDHistoricalTestResults.json?nocache=5")
    county_json = r.text
    regions = pd.read_csv(region_file)
    data = json.loads(county_json)

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

    for date_data in data['historical_county']['values']:
        try:
            date = date_data['testDate']
        except:
            date = date_data['testdate']

        for county in date_data['values']:
            table['date'].append(date)
            table['county'].append(county['County'])
            table['tested'].append(county['total_tested'])
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

    df = pd.DataFrame(table)
    df['date'] = pd.to_datetime(df['date'])
    df = pd.merge(df, regions, how='inner', on='county')
    df = df.drop_duplicates(subset=['date', 'county'])
    df = df.set_index('date')
    df2 = df.pivot(columns='county')

    df2['deaths'] = df2['deaths'].diff(periods=1)
    df2['count'] = df2['count'].diff(periods=1)
    df2['tested'] = df2['tested'].diff(periods=1)
    df2.dropna(inplace=True)
    # Remove outliers and interpolate
    df2.loc[abs(stats.zscore(df2['deaths']['Illinois'])) > 3] = np.nan
    df2 = df2.interpolate().round()
    df2['percentage'] = df2['count'] / df2['tested']
    df2['deaths_per_million'] = 1000000 * df2['deaths'] / df2['population']
    df2['count_per_million'] = 1000000 * df2['count'] / df2['population']

    values = pd.DataFrame(df2)

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


counties = get_regional_breakdown('regions.csv')

N = 256
vals = np.ones((N, 4))
vals[0:29, 0] = np.linspace(76/256, 1, 29)
vals[0:29, 1] = np.linspace(168/256, 253/256, 29)
vals[0:29, 2] = np.linspace(0/256, 148/256, 29)
vals[29:128, 0] = np.linspace(1, 1, 99)
vals[29:128, 1] = np.linspace(253/256, 0, 99)
vals[29:128, 2] = np.linspace(148/256, 0, 99)

vals[128:256, 0] = np.linspace(1, 147/256, 128)
vals[128:256, 1] = np.linspace(0, 85/256, 128)
vals[128:256, 2] = np.linspace(0, 1, 128)
cmap = matplotlib.colors.ListedColormap(vals)


def getmap(df, stat, statname, title, min, max, date):
    plt.close()
    fig = plt.figure(figsize=(7, 8), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

    ax.set_extent([-93, -87, 37, 43], ccrs.Geodetic())
    df = df[df.index == date][stat]

    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_title(title, fontsize=20)

    norm = plt.Normalize(min, max)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm, )
    sm._A = []
    plt.colorbar(sm, ax=ax, shrink=0.6)
    for astate in shpreader.Reader('cb_2018_us_county_5m').records():
        if (astate.attributes['STATEFP'] != '17'):
            continue
        # //print(astate.attributes)
        edgecolor = 'gray'

        # use the name of this state to get pop_density
        try:
            value = df[astate.attributes['NAME']][0]
        except:
            value = 0
            print('Bad '+astate.attributes['NAME'])
        facecolor = cmap(norm(value))
        # # `astate.geometry` is the polygon to plot
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor)

    text = ax.text(x=-93, y=37, s=date.strftime("%m/%d"),
                   transform=ccrs.PlateCarree(), fontsize=70)
    text.set_alpha(0.6)
    plt.savefig('state_map_animation/'+str(date) +
                ' IL County Map '+statname+'.png')


current_date = datetime.datetime.today()
# from_date = current_date - datetime.timedelta(days=window)
# getmap(counties,'count_per_million_14day', 'positivity', 'Positive Testing % {:%m/%d}'.format(current_date), -.2, .30)

date = datetime.datetime(2020, 10, 20)

while ((datetime.datetime.now() - date).days >= 0):
    getmap(counties, 'deaths_per_million_14day',
           'deaths', 'Deaths per Million', 0, 25, date)
    getmap(counties, 'count_per_million_14day', 'positive_cases', 'Positive Cases per Million',
           0, 1200, date)  # getmap(df,'deathIncrease', 'US Deaths per Million',date,-3,3)
    date = date + datetime.timedelta(days=1)
    print(date)
