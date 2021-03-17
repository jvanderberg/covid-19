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
states1 = ['CO', 'IL', 'IA', 'MN', 'ND', 'SD', 'WY',
           'MO', 'MI', 'OH', 'IN', 'NE', 'WY', 'MT', 'MI', 'AR', 'WA', 'OR', 'AZ', 'NM', 'NV', 'UT', 'OK',
           'MS', 'LA', 'AL', 'FL', 'GA', 'SC', 'NC', 'TN', 'KY', 'WV', 'VA', 'NY', 'PA', 'MA', 'RI', 'NJ', 'VT', 'NH', 'ME']
states2 = ['TX', 'CA']
df1 = df[df['state'].isin(states1)].groupby(by='date').sum()
df2 = df[df['state'].isin(states2)].groupby(by='date').sum()
df1 = df1[df1.index >= startdate]
df2 = df2[df2.index >= startdate]

df1['percentage'] = df1['positiveIncrease'] / df1['totalTestResultsIncrease']
df2['percentage'] = df2['positiveIncrease'] / df2['totalTestResultsIncrease']
df1_7day = df1.rolling(window=window).mean()
df2_7day = df2.rolling(window=window).mean()
df1_7day['percentage'] = df1_7day['positiveIncrease'] / \
    df1_7day['totalTestResultsIncrease']
df1_7day['positiveIncrease'] = 1000000 * \
    df1_7day['positiveIncrease'] / df1_7day['population']
df1_7day['deathIncrease_pm'] = 1000000 * \
    df1_7day['deathIncrease'] / df1_7day['population']
df1_7day['totalTestResultsIncrease'] = 1000000 * \
    df1_7day['totalTestResultsIncrease'] / df1_7day['population']
df2_7day['percentage'] = df2_7day['positiveIncrease'] / \
    df2_7day['totalTestResultsIncrease']
df2_7day['positiveIncrease'] = 1000000 * \
    df2_7day['positiveIncrease'] / df2_7day['population']
df2_7day['deathIncrease_pm'] = 1000000 * \
    df2_7day['deathIncrease'] / df2_7day['population']
df2_7day['totalTestResultsIncrease'] = 1000000 * \
    df2_7day['totalTestResultsIncrease'] / df2_7day['population']

colors = ['tab:blue', 'tab:orange', 'tab:red', 'tab:brown',
          'tab:green', 'tab:purple', 'tab:gray', 'tab:cyan', '#ffaaaa', '#aaFFaa']
#######################################################################################
# Deaths per million report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75

plt.plot(df1.index, df1_7day['deathIncrease_pm'],
         color=colors[0], label='Central', linewidth=2)
plt.plot(df2.index, df2_7day['deathIncrease_pm'],
         color=colors[1], label='Other', linewidth=2)
plt.ylabel("Daily Deaths per Million")
current_date = df1_7day.tail(1)['deathIncrease_pm'].index[0]
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
plt.savefig('charts/Regional Death Comparison.png', bbox_inches='tight')

plt.close()
#######################################################################################
# Deaths report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75

plt.plot(df1.index, df1_7day['deathIncrease'],
         color=colors[0], label='Central', linewidth=2)
plt.plot(df2.index, df2_7day['deathIncrease'],
         color=colors[1], label='Other', linewidth=2)
plt.ylabel("Daily Deaths per Day")
current_date = df1_7day.tail(1)['deathIncrease'].index[0]
plt.title('Daily Deaths as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/Regional Deaths Comparison Raw.png', bbox_inches='tight')


#######################################################################################
# Positive cases
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
plt.plot(df1.index, df1_7day['positiveIncrease'],
         color=colors[0], label='Central', linewidth=2)
plt.plot(df2.index, df2_7day['positiveIncrease'],
         color=colors[1], label='Other', linewidth=2)
plt.ylabel("Daily Positives per Million")
plt.legend(loc='best').get_frame().set_linewidth(0.0)

current_date = df1.tail(1)['percentage'].index[0]

plt.title('Daily Positive Cases as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.ylim(0)
# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

plt.savefig('charts/Regional Positives Comparison.png', bbox_inches='tight')


#######################################################################################
# Positive %
#######################################################################################
plt.close()
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
plt.plot(df1.index, df1_7day['percentage'],
         color=colors[0], label='Central', linewidth=2)
plt.plot(df2.index, df2_7day['percentage'],
         color=colors[1], label='Other', linewidth=2)
plt.ylabel("Daily Positive %")
plt.legend(loc='best').get_frame().set_linewidth(0.0)

plt.ylim(0, .5)
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
current_date = df.tail(1)['percentage'].index[0]

plt.title('Daily Positive % as of {:%b %-d}'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

plt.savefig('charts/Regional Positive Pct Comparison.png', bbox_inches='tight')
