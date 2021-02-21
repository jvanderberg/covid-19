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
import datetime
matplotlib.rcParams['text.color'] = '#555555'
matplotlib.rcParams['axes.labelcolor'] = '#555555'
matplotlib.rcParams['xtick.color'] = '#555555'
matplotlib.rcParams['ytick.color'] = '#555555'

window = 14
population = pd.read_csv("population.csv", parse_dates=True)
population = population.set_index('state')
population['population'] = population['population'].astype('int32')

df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",
                 parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df = df[~df['statename'].isnull()]
df['percentage'] = 0
df = df.pivot(columns='statename')
df = df.fillna(value=0)
df = df.rolling(window=window).mean()
df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df['positiveIncrease'] = 1000000 * df['positiveIncrease'] / df['population']
df['deathIncrease'] = 1000000 * df['deathIncrease'] / df['population']
df['hospitalizedIncrease'] = 1000000 * \
    df['hospitalizedIncrease'] / df['population']
df = df.fillna(value=0.0)


def getmap(df, stat, statname, title, min, max, date):
    plt.close()
    fig = plt.figure(figsize=(12, 7), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

    ax.set_extent([-122, -73.5, 22, 50], ccrs.Geodetic())

    shapename = 'admin_1_states_provinces_lakes_shp'
    states_shp = shpreader.natural_earth(resolution='110m',
                                         category='cultural', name=shapename)

    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_title(title, fontsize=20)
    df = df[stat].drop(
        columns=['Puerto Rico', 'District of Columbia', 'Hawaii', 'Alaska'])
    df = df[df.index == date]
    scheme = 'RdYlGn_r'
    cmap = plt.get_cmap(scheme)
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

    newcmap = matplotlib.colors.ListedColormap(vals)
    norm = plt.Normalize(min, max)
    df = df.transpose()
    sm = plt.cm.ScalarMappable(cmap=newcmap, norm=norm)
    sm._A = []
    plt.colorbar(sm, ax=ax, shrink=0.6)
    for astate in shpreader.Reader(states_shp).records():
        edgecolor = 'gray'

        try:
            value = df.loc[astate.attributes['name']][0]
        except:
            value = 0
        facecolor = newcmap(norm(value))
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor, linewidth=0.5)

    text = ax.text(x=-120, y=22, s=date.strftime("%-m/%-d"),
                   transform=ccrs.PlateCarree(), fontsize=70)
    text.set_alpha(0.6)
    plt.savefig('map_animation/'+str(date) + ' ' + title+'.jpg')


date = datetime.datetime(2020, 12, 18)

while ((datetime.datetime.now() - date).days >= 0):
    # getmap(df,'percentage', 'positivity', 'Positive Testing % {:%m/%d}'.format(current_date), -.2, .30)
    getmap(df, 'deathIncrease', 'deaths', 'Daily Deaths per Million',
           0, df['deathIncrease'].max().max(), date)
    getmap(df, 'positiveIncrease', 'positive_cases',
           'Daily Positive Cases per Million', 0, df['positiveIncrease'].max().max(), date)
    date = date + datetime.timedelta(days=1)
    print(date)
