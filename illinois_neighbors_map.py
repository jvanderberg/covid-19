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

states = ['CO','WY','NE','KS','OK','NM','AZ','UT']
statenames = ['Colorado', 'Wyoming', 'Nebraska', 'Kansas', 'Oklahoma', 'New Mexico', 'Arizona','Utah']
statefips= [8, 56, 31, 20, 40, 35, 4, 49]

# states = ['IL','KY','IN','MO','IA','MI','WI']
# statenames = ['Illinois', 'Kentucky', 'Indiana', 'Missouri', 'Iowa', 'Michigan', 'Wisconsin']
# statefips= [17, 21, 18, 29, 19, 26, 55]

lookup = pd.DataFrame({'state': states, 'statename': statenames, 'statefp':statefips}).set_index('statefp')
def get_all_county_data(stat):
    df = pd.read_csv('time_series_covid19_'+stat+'_US.csv')
    df = df[df['Province_State'].isin(statenames)]
    county_data = {}
    data = {}
    for idx,state in enumerate(states):
        county_data[state] = pd.read_csv('counties_'+state+'.csv').set_index(['county','statename'])
        data[state] = df.join(county_data[state],on=['Admin2','Province_State'],how='inner')
    df = data[states[0]]
    for i in range(1,len(states)):
        df = pd.concat([df,data[states[i]]], ignore_index=True)
    date = datetime.datetime(2020,4,1)
    
    cols = []
    while ((datetime.datetime.now() - date).days >= 1):
        try:
            col = date.strftime('%-m/%-d/%y')
            cols.append(col)
            # df[col] = df[col].diff(periods=1)
            # df[col] = df[col].rolling(window=14).mean()
        except:
            print('No date '+col)
        date = date + datetime.timedelta(days= 1)
    cols.append('Province_State')
    cols.append('Admin2')
    df2 = pd.DataFrame(df[cols])
    df2 = df2.set_index(['Admin2','Province_State'])
    df2 = df2.transpose()
    df2 = df2.diff(periods=1)
    df2 = df2.rolling(window=14).mean()
    df2 = df2.transpose()
    df3 = pd.DataFrame(df[['Admin2','Province_State','population']]).set_index(['Admin2','Province_State'])
    df = df2.join(df3)
    return df
    


def getmap(df,statname,title, min, max, date):
    plt.close()
    fig = plt.figure(figsize=(10,9), dpi=400)
    # fig = plt.figure(figsize=(7,8), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())
    # ax.set_extent([-98, -82, 35, 50], ccrs.Geodetic())
 
    ax.set_extent([-115, -94, 30,45], ccrs.Geodetic())
 
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_title(title, fontsize=30)
    shapename = 'admin_1_states_provinces_lakes_shp'
    states_shp = shpreader.natural_earth(resolution='110m',
                                        category='cultural', name=shapename)

    N = 256
    vals = np.ones((N, 4))
    vals[0:29, 0] = np.linspace(76/256, 1, 29)
    vals[0:29, 1] = np.linspace(168/256, 253/256, 29)
    vals[0:29, 2] = np.linspace(0/256, 148/256, 29)
    vals[29:128, 0] = np.linspace( 1, 1, 99)
    vals[29:128, 1] = np.linspace( 253/256, 0, 99)
    vals[29:128, 2] = np.linspace( 148/256, 0, 99)
    
    vals[128:256, 0] = np.linspace(1, 147/256, 128)
    vals[128:256, 1] = np.linspace(0, 85/256, 128)
    vals[128:256, 2] = np.linspace(0, 1, 128)
    cmap = matplotlib.colors.ListedColormap(vals)
    norm = plt.Normalize(min, max)
    sm = plt.cm.ScalarMappable(cmap=cmap,norm=norm, )
    sm._A = []
    plt.colorbar(sm,ax=ax,shrink=0.6)

    for astate in shpreader.Reader('cb_2018_us_county_5m').records():
        statefp = int(astate.attributes['STATEFP'])
        state = None
        try:
            state = lookup.loc[statefp]
        except:
            continue

        edgecolor = 'gray'

        county = astate.attributes['NAME']
        # try:
        value = df.loc[county].loc[state['statename']].loc[date.strftime('%-m/%-d/%y')]
        pop = df.loc[county].loc[state['statename']].loc['population']
        value = 1000000 * (value ) / pop

        # except:
            # value=0
            # print('Bad '+astate.attributes['NAME'])
        facecolor = cmap(norm(value))
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                        facecolor=facecolor, edgecolor=edgecolor)
    
    for astate in shpreader.Reader(states_shp).records():

        edgecolor = 'black'

        ax.add_geometries([astate.geometry], ccrs.PlateCarree(), facecolor='none', edgecolor=edgecolor)


    # text = ax.text(x=-96,y=34,s=date.strftime("%m/%d"), transform=ccrs.PlateCarree(), fontsize=70)

    text = ax.text(x=-102,y=30,s=date.strftime("%m/%d"), transform=ccrs.PlateCarree(), fontsize=70)
    text.set_alpha(0.6)
    plt.savefig('state_map_animation/'+str(date)+' CO Neighbors County Map '+statname+'.png')


current_date = datetime.datetime.today()

counties_confirmed = get_all_county_data('confirmed')
counties_deaths = get_all_county_data('deaths')

date = datetime.datetime(2020,4,16)
while ((datetime.datetime.now() - date).days >= 0):
    getmap(counties_deaths, 'deaths', 'Daily Deaths per Million', 0,25, date)
    getmap(counties_confirmed, 'positive_cases', 'Daily Positive Cases per Million',0, 800, date)    
    date = date + datetime.timedelta(days= 1)
    print(date)

