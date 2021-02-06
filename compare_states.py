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

startdate = datetime.datetime(2020, 4, 1)
matplotlib.rcParams['text.color'] = '#555555'
matplotlib.rcParams['axes.labelcolor'] = '#555555'
matplotlib.rcParams['xtick.color'] = '#555555'
matplotlib.rcParams['ytick.color'] = '#555555'
states = sys.argv[1].split(',')
print(states)
window = 7
population = pd.read_csv("population.csv", parse_dates=True)
population = population.set_index('state')
population['population'] = population['population'].astype('int32')
df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",
                 parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df['percentage'] = 0
df['deathIncrease_pm'] = 0
df = df[df['state'].isin(states)]
df = df[df.index >= startdate]
df = df.pivot(columns='state')

df['percentage'] = df['positiveIncrease'] / df['totalTestResultsIncrease']
df_7day = df.rolling(window=window).mean()
df_7day['percentage'] = df_7day['positiveIncrease'] / \
    df_7day['totalTestResultsIncrease']
df_7day['positiveIncrease'] = 1000000 * \
    df_7day['positiveIncrease'] / df_7day['population']
df_7day['deathIncrease_pm'] = 1000000 * \
    df_7day['deathIncrease'] / df_7day['population']
df_7day['totalTestResultsIncrease'] = 1000000 * \
    df_7day['totalTestResultsIncrease'] / df_7day['population']

colors = ['tab:blue', 'tab:orange', 'tab:red', 'tab:brown',
          'tab:green', 'tab:purple', 'tab:gray', 'tab:cyan', '#ffaaaa', '#aaFFaa']
#######################################################################################
# Deaths per million report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75

for idx, state in enumerate(states):
    plt.plot(df.index, df_7day['deathIncrease_pm'][state],
             color=colors[idx % 10], label=state, linewidth=2)
plt.ylabel("Daily Deaths per Million")
current_date = df_7day.tail(1)['deathIncrease_pm'][state].index[0]
plt.title('Daily Deaths as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.ylim(0)
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/Compare '+sys.argv[1]+' - Deaths.png', bbox_inches='tight')

plt.close()
#######################################################################################
# Deaths report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75

for idx, state in enumerate(states):
    plt.plot(df.index, df_7day['deathIncrease'][state],
             color=colors[idx % 10], label=state, linewidth=2)

plt.ylabel("Daily Deaths per Day")
current_date = df_7day.tail(1)['deathIncrease'][state].index[0]
plt.title('Daily Deaths as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/Compare '+sys.argv[1] +
            ' - Deaths raw.png', bbox_inches='tight')


#######################################################################################
# Positive cases
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
for idx, state in enumerate(states):
    plt.plot(df.index, df_7day['positiveIncrease'][state],
             color=colors[idx % 10], label=state, linewidth=2)
plt.ylabel("Daily Positives per Million")
plt.legend(loc='best').get_frame().set_linewidth(0.0)

current_date = df.tail(1)['percentage'][state].index[0]

plt.title('Daily Positive Cases as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.ylim(0)
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

plt.savefig('charts/Compare '+sys.argv[1] +
            ' - Positives.png', bbox_inches='tight')


#######################################################################################
# Positive %
#######################################################################################
plt.close()
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
for idx, state in enumerate(states):
    plt.plot(df.index, df_7day['percentage'][state],
             color=colors[idx % 10], label=state, linewidth=2)
plt.ylabel("Daily Positive %")
plt.legend(loc='best').get_frame().set_linewidth(0.0)

plt.ylim(0, .5)
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
current_date = df.tail(1)['percentage'][state].index[0]

plt.title('Daily Positive % as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

plt.savefig('charts/Compare '+sys.argv[1] +
            ' - Positive pct.png', bbox_inches='tight')

#######################################################################################
# Completed Test Report
#######################################################################################
plt.close()

plt.figure(1, figsize=(10, 5), dpi=400, clear=True)
for idx, state in enumerate(states):
    plt.plot(df.index, df_7day['totalTestResultsIncrease']
             [state], color=colors[idx % 10], label=state, linewidth=2)
plt.ylabel("Daily Tests per Million")
current_date = df.tail(1)['totalTestResultsIncrease'][state].index[0]
plt.title('Tests Completed per Million as of ' +
          '{:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.ylim(0)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/Compare '+sys.argv[1] +
            ' - Testing.png', bbox_inches='tight')
