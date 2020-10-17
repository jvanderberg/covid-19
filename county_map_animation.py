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
[-122, -73.5, 22, 50]
settings = {'CO' : { 'name': 'Colorado Area', 'states': ['CO','WY','NE','KS','OK','NM','AZ','UT'], 'title_font': 30, 'datex':-102,'datey':30,'figsize':(10,9), 'dpi':400, 'extent':[-115, -94, 30,45]},
            'IL' : { 'name': 'Midwest', 'states': ['OH','MN','IL','KY','IN','MO','IA','MI','WI'], 'title_font': 24, 'datex':-96,'datey':34,'figsize':(7,8), 'dpi':400, 'extent':[-98, -82, 35, 50]},
            'US' : { 'name': 'US', 'states':['AL','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'], 'title_font': 24, 'datex':-120,'datey':22,'figsize':(12,7), 'dpi':400, 'extent':[-122, -73.5, 22, 50]}}


all_state_fips = pd.read_csv('state_fips.csv')
population = pd.read_csv('time_series_covid19_deaths_US.csv')
population = pd.DataFrame({'county': population['Admin2'], 'statename': population['Province_State'], 'population': population['Population']})
population = population.set_index(['county', 'statename'])

def get_all_county_data(setting, fips, stat):
    df = pd.read_csv('time_series_covid19_'+stat+'_US.csv')

    df = df[df['Province_State'].isin(fips['statename'])]
   
    df['county'] = df['Admin2']
    df['statename'] = df['Province_State']
    
    date = datetime.datetime(2020,4,1)
    
    cols = []
    while ((datetime.datetime.now() - date).days >= 1):
        try:
            col = date.strftime('%-m/%-d/%y')
            cols.append(col)
        except:
            print('No date '+col)
        date = date + datetime.timedelta(days= 1)
    cols.append('statename')
    cols.append('county')
    df2 = pd.DataFrame(df[cols])
    df2 = df2.set_index(['county','statename'])
    df2 = df2.transpose()
    df2 = df2.diff(periods=1)
    df2 = df2.rolling(window=14).mean()

    max = df2.max().max()
    print('Max value for stat: '+stat+' = '+str(max))
    stats=df2.max().describe()
    print(stats)
    df2 = df2.transpose()
    df = df2.join(population)
    return df,stats
    


def getmap(setting, fips, df,statname,title, min, max, date):
    lookup = fips.set_index('FIPS')
    plt.close()
    #fig = plt.figure(figsize=(10,9), dpi=400)
    fig = plt.figure(figsize=setting['figsize'], dpi=setting['dpi'])
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())
    ax.set_extent(setting['extent'], ccrs.Geodetic())
 
    #ax.set_extent([-115, -94, 30,45], ccrs.Geodetic())
 
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_title(title, fontsize=setting['title_font'])
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

        edgecolor = 'white'

        county = astate.attributes['NAME']
        try:
            value = df.loc[county].loc[state['statename']].loc[date.strftime('%-m/%-d/%y')]
            pop = df.loc[county].loc[state['statename']].loc['population']
            value = 1000000 * (value ) / pop

        except:
            value=0
            # print('Bad '+astate.attributes['NAME']+' '+state['statename'])
        facecolor = cmap(norm(value))
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                        facecolor=facecolor, edgecolor=edgecolor, linewidth=0.2)
    
    for astate in shpreader.Reader(states_shp).records():

        edgecolor = .2,.2,.2

        ax.add_geometries([astate.geometry], ccrs.PlateCarree(), facecolor='none', edgecolor=edgecolor, linewidth=1)


    text = ax.text(x=setting['datex'],y=setting['datey'],s=date.strftime("%m/%d"), transform=ccrs.PlateCarree(), fontsize=70)

    #text = ax.text(x=-102,y=30,s=date.strftime("%m/%d"), transform=ccrs.PlateCarree(), fontsize=70)
    text.set_alpha(0.6)
    plt.savefig('state_map_animation/'+str(date)+' '+setting['name']+' '+statname+'.png')



setting = settings['US']
state_fips = all_state_fips[all_state_fips['state'].isin(setting['states'])] 

current_date = datetime.datetime.today()

counties_confirmed, cases_stats = get_all_county_data(setting,state_fips,'confirmed')
counties_deaths,death_stats = get_all_county_data(setting,state_fips,'deaths')

date = datetime.datetime(2020,4,16)
while ((datetime.datetime.now() - date).days >= 1):
    print(date)
    getmap(setting, state_fips, counties_deaths, 'deaths', 'Daily Deaths per Million', 0,death_stats['std']*10, date)
    getmap(setting, state_fips, counties_confirmed, 'positive_cases', 'Daily Positive Cases per Million',0, cases_stats['std'] * 10, date)    
    date = date + datetime.timedelta(days= 1)

