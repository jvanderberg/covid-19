import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

df = pd.read_csv('us_daily.csv', index_col=0, parse_dates=True)

date_from = datetime.datetime(2020,3,1)
df = df[df.index > date_from ]
#######################################################################################
# Positives/Positive testing %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)

p1 = plt.plot(df.index, df['deathIncrease_7day'], color='#EE2222', label="Daily Deaths")
plt.ylabel("Daily Deaths")
plt.ylim(0)
plt.legend(loc=9)

ax2 = plt.twinx()
ax2.plot(df.index, df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day'], color='#6688cc', label="% Positive")
ax2.set_ylim(0)
ax2.set_ylabel("% Positive")
ax2.margins(0)

ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.legend(loc='best').set_zorder(10)
current_value = df.tail(1)['deathIncrease_7day'].round()[0]
current_date = df.tail(1)['deathIncrease_7day'].index[0]
current_value_percentage =(df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day']).tail(1)[0]

plt.title('US Daily Positive Cases and Deaths - '+'{:%b %-d} - {:,} Deaths - {:0.1f}% positive'.format(current_date,int(current_value), 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('US Death and positives.png', bbox_inches='tight')
plt.close()
