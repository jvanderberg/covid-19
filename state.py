import json
import datetime
import pandas as pd
import numpy as np
import requests
from scipy import stats
min_population = 0
population = pd.read_csv("population.csv", parse_dates=True)
population = population.set_index('state')
population['population'] = population['population'].astype('int32')
df = pd.read_csv("covid-tracking.csv",
                 parse_dates=True, index_col='date')
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
df = df.pivot(columns='state')
rolling = df.rolling(window=14, center=True).mean()

export = df.join(rolling, rsuffix="_14day_centered")
export.to_csv('state_daily.csv')
# Get deaths only
df = pd.DataFrame(export['deathIncrease_14day_centered'])
states = []
maxxes = []
day = []
for state in df.columns:
    max = df[state].max()
    worst_day = df[df[state] == max]
    print(state, max, worst_day.index[0])
    states.append(state)
    maxxes.append(max)
    day.append(worst_day.index[0])

worst = pd.DataFrame({'state': states, 'max': maxxes, 'worst_date': day})
worst = worst.set_index('worst_date')
worst = worst.sort_index()
df.to_csv('state_deaths_daily_14day_centered.csv')

df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv",
                 parse_dates=True, index_col='date')
df = df[['state', 'deathIncrease', 'positiveIncrease',
         'totalTestResultsIncrease', 'hospitalizedIncrease']]
df = df.sort_index(ascending=True)
df = df.join(population, on='state')
worst = worst.reset_index()
worst = worst.set_index('state')
df = df.join(worst, on='state')
df = df[df['population'] > min_population]

first = df[df['worst_date'] < datetime.datetime(2020, 7, 1)]
second = df[df['worst_date'] > datetime.datetime(2020, 6, 30)]
third = second[second['worst_date'] > datetime.datetime(2020, 8, 31)]
second = second[second['worst_date'] < datetime.datetime(2020, 9, 1)]

first_totals = first.groupby('date').sum()
first_totals = first_totals.rolling(window=7).mean()
second_totals = second.groupby('date').sum()
second_totals = second_totals.rolling(window=7).mean()
third_totals = third.groupby('date').sum()
third_totals = third_totals.rolling(window=7).mean()

print('First:')
print((first['state'].unique()))
print('Second:')
print((second['state'].unique()))
print('Third:')
print((third['state'].unique()))


first_totals['deaths_per_million'] = 1000000 * \
    first_totals['deathIncrease']/first_totals['population']
second_totals['deaths_per_million'] = 1000000 * \
    second_totals['deathIncrease']/second_totals['population']
third_totals['deaths_per_million'] = 1000000 * \
    third_totals['deathIncrease']/third_totals['population']
df['deaths_per_million'] = 1000000 * df['deathIncrease']/df['population']
stats = ['deathIncrease', 'positiveIncrease', 'totalTestResultsIncrease',
         'hospitalizedIncrease', 'deaths_per_million']
df = df.pivot(columns='state')
for stat in stats:
    df[stat] = df[stat].rolling(window=14, center=True).mean()

df.to_csv('state_daily_14day_centered.csv')

final = second_totals.join(
    third_totals, lsuffix='second', rsuffix='third').join(first_totals)

final.to_csv('state_first_second_wave.csv')
