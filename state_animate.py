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
population = pd.read_csv("population.csv",parse_dates=True)
population = population.set_index('state')
population['population'] = population['population'].astype('int32')

df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df = df[~df['statename'].isnull()]
df['percentage'] = 0
df = df.pivot(index=df.index, columns='statename')
df = df.fillna(value=0)
df = df.rolling(window=window).mean()
df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df['positiveIncrease'] = 1000000* df['positiveIncrease'] / df['population']
df['deathIncrease'] = 1000000* df['deathIncrease'] / df['population']
df['hospitalizedIncrease'] = 1000000* df['hospitalizedIncrease'] / df['population']
df = df.fillna(value=0.0)
# df = df.replace(to_replace=0, value=0.1)
# df[df < 0.1] = 0.1
def getmap(data,stat,title,date,minz,maxz):
    plt.close()
    fig = plt.figure(figsize=(10,6), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

    ax.set_extent([-125, -66.5, 20, 50], ccrs.Geodetic())
    shapename = 'admin_1_states_provinces_lakes_shp'
    states_shp = shpreader.natural_earth(resolution='110m',
                                        category='cultural', name=shapename)

    #df = np.log(data[stat])
    df = data[stat]
    # max = df.max().max()
    # min = df.min().min()
    zscore = stats.zscore(df, axis=None)
    for index, col in enumerate(df.columns):
        df[col+'_zscore'] = zscore[:,index]

    # df.to_csv('temp.csv')
    df=df[df.index==date]
    # df = df.transpose()
    # df['zscore'] = stats.zscore(df)


    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)

    ax.set_title(title, fontsize=20)

    scheme = 'RdYlGn'
    cmap=plt.get_cmap(scheme)

    max = np.max(zscore)
    min = np.min(zscore)
    norm = plt.Normalize(minz, maxz)
    # df = df.transpose()
    #for state in shpreader.Reader(states_shp).geometries():
    for astate in shpreader.Reader(states_shp).records():

        ### You want to replace the following code with code that sets the
        ### facecolor as a gradient based on the population density above
        #facecolor = [0.9375, 0.9375, 0.859375]

        edgecolor = 'black'

        try:
            val = df[astate.attributes['name']+'_zscore'].iloc[0]
            # use the name of this state to get pop_density
            value = val
        except:
            value = 0

        facecolor = cmap(1-norm(value))
        # `astate.geometry` is the polygon to plot
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                        facecolor=facecolor, edgecolor=edgecolor)
    text = ax.text(x=-120,y=22,s=date.strftime("%m/%d"), transform=ccrs.PlateCarree(), fontsize=70)
    text.set_alpha(0.6)

    plt.savefig('charts/map_animation/'+str(date) + ' ' +title+'.jpg')

date = datetime.datetime(2020,3,1)

while ((datetime.datetime.now() - date).days >= 0):
    #getmap(df,'deathIncrease', 'US Deaths per Million',date,-3,3)
    getmap(df,'positiveIncrease', 'US Positive Cases per Million',date,-3,3)
    date = date + datetime.timedelta(days= 1)
    print(date)