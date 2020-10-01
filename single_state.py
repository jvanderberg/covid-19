import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib
import sys

matplotlib.rcParams['text.color'] = '#555555'
matplotlib.rcParams['axes.labelcolor'] = '#555555'
matplotlib.rcParams['xtick.color'] = '#555555'
matplotlib.rcParams['ytick.color'] = '#555555'
state = sys.argv[1]
window = 7
population = pd.read_csv("population.csv",parse_dates=True)
population = population.set_index('state')
population['population'] = population['population'].astype('int32')
df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df['percentage'] = 0
df = df[df['state'] == state]
df = df.pivot(index=df.index, columns='state')
df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']

df_7day = df.rolling(window=window).mean()
df_7day['percentage'] = df_7day['positiveIncrease'] / df_7day['totalTestResultsIncrease']

#######################################################################################
# Deaths report
#######################################################################################
plt.figure(1,figsize=(10, 5), dpi=400)
width = 0.75
p1 = plt.bar(df.index, df['deathIncrease'][state], width, color='#6688cc', label="Daily Deaths")
plt.plot(df.index, df_7day['deathIncrease'][state], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Deaths")
current_value = df_7day.tail(1)['deathIncrease'][state].round()[0]
current_date = df_7day.tail(1)['deathIncrease'][state].index[0]
plt.title(state+' Daily Deaths - '+'{:%b %-d} - {:0.0f} deaths per day'.format(current_date,current_value))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('Single State - '+state + ' Deaths.png', bbox_inches='tight')

#######################################################################################
# Hospitalized report
#######################################################################################
plt.close()
plt.figure(1,figsize=(10, 5), dpi=400)
width = 0.75
p1 = plt.bar(df.index, df['hospitalizedIncrease'][state], width, color='#6688cc', label="Daily Hospitalized")
plt.plot(df.index, df_7day['hospitalizedIncrease'][state], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Hospitalization")
current_value = df_7day.tail(1)['hospitalizedIncrease'][state].round()[0]
current_date = df_7day.tail(1)['hospitalizedIncrease'][state].index[0]
plt.title(state+' Daily Hospitalized - '+'{:%b %-d} - {:0.0f} per per day'.format(current_date,current_value))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('Single State - '+state + ' Hospitalized.png', bbox_inches='tight')

#######################################################################################
# Positives/Positive testing %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)

p1 = plt.bar(df.index, df['positiveIncrease'][state], width, color='#6688cc', label="Daily Positives")
plt.plot(df.index, df_7day['positiveIncrease'][state], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Positives")
plt.legend(loc=9).get_frame().set_linewidth(0.0)

ax2 = plt.twinx()
ax2.plot(df.index, df_7day['percentage'][state], color='#cca80a', label="% Positive", linewidth=3)
ax2.set_ylim(0)
ax2.set_ylabel("% Positive")
ax2.margins(0)

ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.legend(loc='best').set_zorder(10)
ax2.legend().get_frame().set_linewidth(0.0)
current_value = df_7day.tail(1)['positiveIncrease'][state].round()[0]
current_date = df.tail(1)['percentage'][state].index[0]
current_value_percentage = df_7day.tail(1)['percentage'][state][0]

plt.title(state + ' Daily Positive cases - '+'{:%b %-d} - {:,} cases per day - {:0.1f}% positive'.format(current_date,int(current_value), 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('Single State - '+state+' Positives.png', bbox_inches='tight')

#######################################################################################
# Completed Test Report
#######################################################################################
plt.close()

plt.figure(1,figsize=(10, 5), dpi=400, clear=True)
width = 0.75
p1 = plt.bar(df.index, df['totalTestResultsIncrease'][state], width, color='#6688cc', label="Tests Completed")
plt.plot(df.index, df_7day['totalTestResultsIncrease'][state], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Tests")
current_value = df_7day.tail(1)['totalTestResultsIncrease'][state].round()[0]
current_date = df.tail(1)['totalTestResultsIncrease'][state].index[0]
plt.title(state+' Tests Completed - '+'{:%b %-d} - {:,} test per day'.format(current_date,int(current_value)))
plt.grid(axis='y', linewidth=0.5)

# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('Single State - ' + state +' Testing.png', bbox_inches='tight')
