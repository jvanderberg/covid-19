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

window = 14
population = pd.read_csv("population.csv", parse_dates=True)
population = population.set_index('state')
population['population'] = population['population'].astype('int32')
df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",
                 parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df['percentage'] = 0
df = df.pivot(columns='state')
df = df.rolling(window=window).mean()
current_date = df.tail(1)['deathIncrease']['TX'].index[0]
df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df['positiveIncrease'] = 1000000 * df['positiveIncrease'] / df['population']
df['deathIncrease'] = 1000000 * df['deathIncrease'] / df['population']
df['hospitalizedIncrease'] = 1000000 * \
    df['hospitalizedIncrease'] / df['population']
df = df[df.index >= datetime.datetime(2020, 4, 1)]


def do_sort(df, stat):
    today = df.iloc[-1][stat]
    lastweek = df.iloc[0-window-1][stat]
    diff = today - lastweek
    df2 = pd.DataFrame({'today': today, "lastweek": lastweek, "diff": diff})
    df2 = df2.sort_values(by='diff')
    df2.dropna(inplace=True)
    return df2


def do_chart(df_sorted, df, stat='deathIncrease', name='Death Per Million', percentage=False):

    items = df_sorted.index.values
    df_sorted['zscore'] = np.abs(stats.zscore(df_sorted['diff']))

    length = len(items)
    rows = length
    plt.close()
    plt.figure(1, dpi=200, clear=True)
    f, ax = plt.subplots(rows, sharey=True, sharex=True)
    maxValue = df[stat].max().max()

    plt.rc('font', size=22)          # controls default text sizes
    for row in range(0, rows):

        item = items[row]
        print(row, item)
        current_value = df_sorted[df_sorted.index == item]['today'][0]
        change = df_sorted[df_sorted.index == item]['diff'][0]
        zscore = df_sorted[df_sorted.index == item]['zscore'][0]
        if (zscore <= 0.5):
            chars = 1
        elif (zscore <= 2):
            chars = 2
        else:
            chars = 3

        ax[row].plot(df.index, df[stat][item], linewidth=4, color='#6688cc')
        if (percentage):
            ax[row].text(df.index[0], maxValue/5, item+' {:0.1f}%  '.format(
                100*change)+('  '*chars), fontsize=20, ha='right', va='bottom')
            ax[row].text(df.index[-1], maxValue/5, '{:0.1f}%'.format(
                100*current_value), fontsize=20, ha='right', va='bottom')
        else:
            ax[row].text(df.index[0], maxValue/5, item+' {:0.2f}  '.format(
                change)+('  '*chars), fontsize=20, ha='right', va='bottom')
            ax[row].text(df.index[-1], maxValue/5, '{:0.1f}'.format(
                current_value), fontsize=20, ha='right', va='bottom')

        if (change > 0):
            ax[row].text(df.index[0], maxValue/5, '\u25b2' * chars,
                         color='#CC2222', fontsize=20, ha='right', va='bottom')
        else:
            ax[row].text(df.index[0], maxValue/5, '\u25bc' * chars,
                         color='#22CC22', fontsize=20, ha='right', va='bottom')

        ax[row].set_ylim(0, maxValue)

        for k, v in ax[row].spines.items():
            v.set_visible(False)
        ax[row].set_xticks([])
        ax[row].set_yticks([])

    print('Setting height...')
    f.set_figheight(2 * rows)
    f.set_figwidth(8)
    print('Setting layout...')
    f.tight_layout(pad=0, w_pad=0, h_pad=0)
    f.suptitle(name)
    print('Saving...')
    plt.savefig('charts/State Ranking '+name+'.png')

# do_chart(df_sorted = do_sort(df=df, stat='positiveIncrease'),df=df,stat='positiveIncrease', name="Positive Cases Per Million")
# do_chart(df_sorted = do_sort(df=df, stat='percentage'),df=df,stat='percentage', name="Positivity Percentage", percentage=True)
#do_chart(df_sorted = do_sort(df=df, stat='deathIncrease'),df=df,stat='deathIncrease', name="Deaths Per Million")
# do_chart(df_sorted = do_sort(df=df, stat='hospitalizedIncrease'),df=df,stat='hospitalizedIncrease', name="Hospitalized per Million")


df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",
                 parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df = df[~df['statename'].isnull()]
df['percentage'] = 0
df = df.pivot(columns='statename')
df = df.rolling(window=window).mean()

df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df['positiveIncrease'] = 1000000 * df['positiveIncrease'] / df['population']
df['deathIncrease'] = 1000000 * df['deathIncrease'] / df['population']
df['hospitalizedIncrease'] = 1000000 * \
    df['hospitalizedIncrease'] / df['population']


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


def getmap(df, stat, statname, title, min, max):
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
    df = df.iloc[-1]
    df.to_csv('us_'+statname+'.csv')
    norm = plt.Normalize(0, df.max())
    df = df.transpose()
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    plt.colorbar(sm, ax=ax, shrink=0.6)
    for astate in shpreader.Reader(states_shp).records():
        edgecolor = 'gray'

        try:
            value = df[astate.attributes['name']]
        except:
            value = 0

        facecolor = cmap(norm(value))
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor)

    plt.savefig('charts/US Map of '+statname+'.png')


from_date = current_date - datetime.timedelta(days=window)
getmap(df, 'percentage', 'positivity',
       'Positive Testing % {:%m/%d}'.format(current_date), -.2, .30)
getmap(df, 'deathIncrease', 'deaths',
       'Deaths per Million {:%m/%d}'.format(current_date), -3, 6)
getmap(df, 'positiveIncrease', 'positive_cases',
       'Positive Cases per Million {:%m/%d}'.format(current_date), -200, 400)

df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df['percentage'] = df['percentage'].diff(periods=14)
df['positiveIncrease'] = df['positiveIncrease'].diff(periods=14)
df['deathIncrease'] = df['deathIncrease'].diff(periods=14)

N = 256
vals = np.ones((N, 4))
vals[0:128, 0] = np.linspace(0, 1, 128)
vals[0:128, 1] = np.linspace(1, 1, 128)
vals[0:128, 2] = np.linspace(0, 1, 128)
vals[128:256, 0] = np.linspace(1, 1, 128)
vals[128:256, 1] = np.linspace(1, 0, 128)
vals[128:256, 2] = np.linspace(1, 0, 128)
cmap = matplotlib.colors.ListedColormap(vals)


def getmap_diff(df, stat, statname, title, min, max):
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
    df = df.iloc[-1]
    df.to_csv('us_14_day_change_in_'+statname+'.csv')
    norm = plt.Normalize(min, max)
    df = df.transpose()
    print(stat + ' ' + str(df.min()))
    print(stat + ' ' + str(df.max()))
    # cmap = plt.get_cmap('RdYlGn_r')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    plt.colorbar(sm, ax=ax, shrink=0.6)
    for astate in shpreader.Reader(states_shp).records():
        edgecolor = 'gray'

        try:
            value = df[astate.attributes['name']]
        except:
            value = 0

        facecolor = cmap(norm(value))
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor)

    plt.savefig('charts/US Two Week Change Map of '+statname+'.png')


getmap_diff(df, 'percentage', 'positivity',
            'Positive Testing % - Last Two Weeks - {:%m/%d}'.format(current_date), -.1, .1)
getmap_diff(df, 'deathIncrease', 'deaths',
            'Change in Daily Deaths per Million - Last Two Weeks - {:%m/%d}'.format(current_date), -6, 6)
getmap_diff(df, 'positiveIncrease', 'positive_cases',
            'Change in Daily Positive Cases per Million - Last Two Weeks - {:%m/%d}'.format(current_date), -500, 500)
