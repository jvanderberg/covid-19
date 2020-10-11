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

states = ['IL','KY','IN','MO','IA','MI','WI']
statenames = ['Illinois', 'Kentucky', 'Indiana', 'Missouri', 'Iowa', 'Michigan', 'Wisconsin']
statefips= [17, 21, 18, 29, 19, 26, 55]

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
    while ((datetime.datetime.now() - date).days >= 2):
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
    # df.melt(id_vars=['Province_State','Admin2'], var_name='date', value_name='deaths')
    df3 = pd.DataFrame(df[['Admin2','Province_State','population']]).set_index(['Admin2','Province_State'])
    df = df2.join(df3)
    return df
    


def getmap(df,stat,statname,title, min, max, date):
    plt.close()
    fig = plt.figure(figsize=(7,8), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

    ax.set_extent([-98, -82, 35, 50], ccrs.Geodetic())
 
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_title(title, fontsize=20)

    scheme = 'RdYlGn_r'
    cmap=plt.get_cmap(scheme)
    norm = plt.Normalize(min, max)
    sm = plt.cm.ScalarMappable(cmap=cmap,norm=norm, )
    sm._A = []
    plt.colorbar(sm,ax=ax,shrink=0.6, boundaries=np.arange(0, max, max/100))
    for astate in shpreader.Reader('cb_2018_us_county_5m').records():
        statefp = int(astate.attributes['STATEFP'])
        state = None
        try:
            state = lookup.loc[statefp]
        except:
            continue

        if (statefp == 17):
            edgecolor = 'black'
        else:
            edgecolor = 'gray'

        county = astate.attributes['NAME']
        # use the name of this state to get pop_density
        # previousdate = date - datetime.timedelta(days=1)
        try:
            # lastvalue = df.loc[county].loc[state['statename']].loc[previousdate.strftime('%-m/%-d/%y')]
            value = df.loc[county].loc[state['statename']].loc[date.strftime('%-m/%-d/%y')]
            pop = df.loc[county].loc[state['statename']].loc['population']
            value = 1000000 * (value ) / pop
            print(value)

        except:
            value=0
            print('Bad '+astate.attributes['NAME'])
        facecolor = cmap(norm(value))
        # # `astate.geometry` is the polygon to plot
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                        facecolor=facecolor, edgecolor=edgecolor)
    
    text = ax.text(x=-93,y=37,s=date.strftime("%m/%d"), transform=ccrs.PlateCarree(), fontsize=70)
    text.set_alpha(0.6)
    plt.savefig('state_map_animation/'+str(date)+' IL Neighbors County Map '+statname+'.png')
current_date = datetime.datetime.today()

counties_confirmed = get_all_county_data('confirmed')
counties_deaths = get_all_county_data('deaths')

print(1)
date = datetime.datetime(2020,10,8)
getmap(counties_deaths,'deaths_per_million_14day', 'deaths', 'Deaths per Million', -15, 25, date)
getmap(counties_confirmed,'count_per_million_14day', 'positive_cases', 'Positive Cases per Million',-200, 400, date)    
#getmap(df,'deathIncrease', 'US Deaths per Million',date,-3,3)

# while ((datetime.datetime.now() - date).days >= 0):
#     getmap(counties,'count_per_million_14day', 'positive_cases', 'Positive Cases per Million',-200, 400, date)    #getmap(df,'deathIncrease', 'US Deaths per Million',date,-3,3)
#     date = date + datetime.timedelta(days= 1)
#     print(date)
