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
df['percentage'] = 0
df = df.pivot(index=df.index, columns='state')
df = df.rolling(window=window).mean()
df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df['positiveIncrease'] = 1000000* df['positiveIncrease'] / df['population']
df['deathIncrease'] = 1000000* df['deathIncrease'] / df['population']
df['hospitalizedIncrease'] = 1000000* df['hospitalizedIncrease'] / df['population']
df = df[df.index >= datetime.datetime(2020,4,1)]

def do_sort(df, stat):
    today = df.iloc[-1][stat]
    lastweek = df.iloc[0-window-1][stat]
    diff = today - lastweek
    df2 = pd.DataFrame({'today': today, "lastweek": lastweek, "diff": diff})
    df2 = df2.sort_values(by='diff')
    df2.dropna(inplace=True)
    return df2


def do_chart(df_sorted, df, stat = 'deathIncrease', name='Death Per Million', percentage=False):
    
    items = df_sorted.index.values
    df_sorted['zscore'] = np.abs(stats.zscore(df_sorted['diff']))

    

    length = len(items)
    rows = length
    plt.close()
    plt.figure(1, dpi=200, clear=True)
    f, ax = plt.subplots(rows,sharey=True, sharex=True)
    maxValue = df[stat].max().max()


    plt.rc('font', size=22)          # controls default text sizes
    for row in range(0,rows):

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

        ax[row].plot(df.index, df[stat][item],linewidth=4, color='#6688cc')
        if (percentage):
            ax[row].text(df.index[0],maxValue/5,item+' {:0.1f}%  '.format(100*change)+('  '*chars),fontsize=20, ha='right', va='bottom')
            ax[row].text(df.index[-1],maxValue/5,'{:0.1f}%'.format(100*current_value),fontsize=20, ha='right', va='bottom')
        else:
            ax[row].text(df.index[0],maxValue/5,item+' {:0.2f}  '.format(change)+('  '*chars),fontsize=20, ha='right', va='bottom')
            ax[row].text(df.index[-1],maxValue/5,'{:0.1f}'.format(current_value),fontsize=20, ha='right', va='bottom')

        if (change > 0):
            ax[row].text(df.index[0],maxValue/5, '\u25b2' * chars,color='#CC2222', fontsize=20, ha='right', va='bottom')
        else:
            ax[row].text(df.index[0],maxValue/5, '\u25bc' * chars,color='#22CC22', fontsize=20, ha='right', va='bottom')

        ax[row].set_ylim(0,maxValue)

        for k,v in ax[row].spines.items():
            v.set_visible(False)
        ax[row].set_xticks([])
        ax[row].set_yticks([])

    print('Setting height...')
    f.set_figheight(2* rows)
    f.set_figwidth(8)
    print('Setting layout...')
    f.tight_layout(pad=0, w_pad=0, h_pad=0)
    f.suptitle(name)
    print('Saving...')    
    plt.savefig('State Ranking '+name+'.png')

do_chart(df_sorted = do_sort(df=df, stat='positiveIncrease'),df=df,stat='positiveIncrease', name="Positive Cases Per Million")

do_chart(df_sorted = do_sort(df=df, stat='percentage'),df=df,stat='percentage', name="Positivity Percentage", percentage=True)
do_chart(df_sorted = do_sort(df=df, stat='deathIncrease'),df=df,stat='deathIncrease', name="Deaths Per Million")
do_chart(df_sorted = do_sort(df=df, stat='hospitalizedIncrease'),df=df,stat='hospitalizedIncrease', name="Hospitalized per Million")




