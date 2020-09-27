import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib

matplotlib.rcParams['text.color'] = '#555555'
matplotlib.rcParams['axes.labelcolor'] = '#555555'
matplotlib.rcParams['xtick.color'] = '#555555'
matplotlib.rcParams['ytick.color'] = '#555555'



df = pd.read_csv('regional_north_south.csv', header=[0,1], index_col=0, parse_dates=True)


#######################################################################################
# Regional Deaths Per Million
#######################################################################################
items = [ 'Illinois', 'North', 'South']

plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3, sharex=False, sharey=True)
june_plus = df[df.index > datetime.datetime(2020,4,30)]
for col in range(0,3):
    item = items[col]
    current_value = df.tail(1)['deaths_per_million_7day'][item][0]

    ax[col].plot(june_plus.index, june_plus['deaths_per_million_7day'][item], color='#6688cc', linewidth=3)
    ax[col].set_title(item +' - {:0.1f}'.format(current_value), fontsize=18)
    ax[col].grid(axis='y', linewidth=0.5)
    ax[col].set_ylim(0,10)
    ax[col].spines["top"].set_visible(False)
    ax[col].spines["right"].set_visible(False)
    ax[col].spines["left"].set_visible(False)
    ax[col].spines["bottom"].set_visible(False)
    ax[col].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 
    ax[col].xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 


f.set_figheight(16)
f.set_figwidth(8)
f.tight_layout(pad=6, w_pad=1, h_pad=5)
f.suptitle('Illinois North/South Death Rates Per Million - 7 Day Average', fontsize=18)
# Format the date into months & days

# Change the tick interval
plt.box(False)

#plt.margins(0)
plt.savefig('North-South deaths per Million.png', dpi=200)