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
    r = requests.get("https://www.dph.illinois.gov/sitefiles/COVIDHistoricalTestResults.json?nocache=5")
    county_json= r.text
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
        date = date_data['testDate']
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
    df = pd.merge(df,regions,how='inner', on='county')
    df = df.drop_duplicates(subset=['date','county'])
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
    df2['deaths_per_million_7day'] = 1000000 * df2['deaths_7day'] / df2['population']
    df2['count_per_million_7day'] = 1000000 * df2['count_7day'] / df2['population']

    df2['deaths_14day'] = df2['deaths'].rolling(window=14).mean()
    df2['count_14day'] = df2['count'].rolling(window=14).mean()
    df2['tested_14day'] = df2['tested'].rolling(window=14).mean()
    df2['percentage_14day'] = df2['count_14day'] / df2['tested_14day']
    df2['deaths_per_million_14day'] = 1000000 * df2['deaths_14day'] / df2['population']
    df2['count_per_million_14day'] = 1000000 * df2['count_14day'] / df2['population']
    return df2
    
counties = get_regional_breakdown('regions.csv')


def getmap(df,stat,statname,title, min, max):
    plt.close()
    fig = plt.figure(figsize=(7,8), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

    ax.set_extent([-93, -87, 37, 43], ccrs.Geodetic())

    # shapename = 'admin_1_states_provinces_lakes_shp'
    # states_shp = shpreader.natural_earth('cb_2018_us_county_20m.shp')


    # df = do_sort(df,stat)
    # df = df[['diff']]
    # df['zscore'] = stats.zscore(df)

    df = df[stat].tail(1)
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_title(title, fontsize=20)

    scheme = 'RdYlGn_r'
    cmap=plt.get_cmap(scheme)
    # df = df[stat].drop(columns=['Puerto Rico', 'District of Columbia', 'Hawaii', 'Alaska'])
    # df = df.iloc[-1]
    # df.to_csv('us_change_in_'+statname+'.csv')
    # max = df.max()
    # min = df.min()
    norm = plt.Normalize(min, max)
    # ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(scheme))
    #for state in shpreader.Reader(states_shp).geometries():
    sm = plt.cm.ScalarMappable(cmap=cmap,norm=norm, )
    sm._A = []
    plt.colorbar(sm,ax=ax,shrink=0.6, boundaries=np.arange(0, max, max/100))
    for astate in shpreader.Reader('cb_2018_us_county_5m').records():
        if (astate.attributes['STATEFP']!='17'):
            continue
        # //print(astate.attributes)
        edgecolor = 'gray'

        # use the name of this state to get pop_density
        try:
            value = df[astate.attributes['NAME']][0]
        except:
            value=0
            print('Bad '+astate.attributes['NAME'])
        print(value)
        facecolor = cmap(norm(value))
        # # `astate.geometry` is the polygon to plot
        ax.add_geometries([astate.geometry], ccrs.PlateCarree(),
                        facecolor=facecolor, edgecolor=edgecolor)

    plt.savefig('charts/IL County Map'+statname+'.png')
current_date = datetime.datetime.today()
# from_date = current_date - datetime.timedelta(days=window)
# getmap(counties,'count_per_million_14day', 'positivity', 'Positive Testing % {:%m/%d}'.format(current_date), -.2, .30)
getmap(counties,'deaths_per_million_14day', 'deaths', 'Deaths per Million {:%m/%d}'.format(current_date), -15, 25)
getmap(counties,'count_per_million_14day', 'positive_cases', 'Positive Cases per Million {:%m/%d}'.format(current_date),-200, 400)