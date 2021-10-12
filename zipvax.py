import requests
import re
import pandas as pd
import datetime
import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib

# population data from here https://www.actforchildren.org/about/research-data/data

df = pd.read_csv("https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/getCOVIDVaccineAdministrationZIP?format=csv", parse_dates=['Report_Date'], skiprows=1)
population = pd.read_csv('cook_zipcodes.csv').set_index('zip')
df = df.rename(columns={'ZipCode':'zip'})
df = df.set_index('zip').join(population, on='zip', how='inner')
df['first'] = df['FirstDoseCount'].astype(float)
df['full'] = df['FullyVaccinatedCount'].astype(float)
df = df.groupby(by=['city']).sum()
df['fullpct'] = df['full']/df['population']
df['ineligible'] = df['Age 0-2']+df['Age 3-4'] + df['Age 5'] + df['Age 6-12']
df['eligible'] = df['population'] - df['ineligible']
df['eligiblefullpct'] = df['full']/df['eligible']


df = df.reset_index()
df = df.sort_values(by=['population'])
df.to_csv('zip_vax.csv')
df = df[df['population'] > 30000]
df = df.sort_values(by=['fullpct'])

plt.figure(figsize=(10, 8), dpi=400)
plt.box(0)
plt.margins(0)
width = 0.75
p1 = plt.barh(df['city'], df['fullpct'], width,
              color='#6688cc', label="Fully Vaccinated % of total population")
plt.legend(loc='best')
plt.legend().get_frame().set_linewidth(0.0)
plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.title('Cook County Full Vaccination Percentage (pop > 30k)')
plt.grid(axis='x', linewidth=0.5)
# plt.xticks([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
for x, y in zip(df['city'], df['fullpct']):

    label = "{:0.1f}%".format(100*y)

    plt.annotate(label,  # this is the text
                 (y, x),  # this is the point to label
                 textcoords="offset points",  # how to position the text
                 xytext=(20, -3),  # distance from text to points (x,y)
                 ha='center')  # horizontal alignment can be left, right or center

plt.savefig('charts/Cook Municipal Full Vaccination Ranking.png', bbox_inches='tight')
plt.close()


df = df.sort_values(by=['eligiblefullpct'])

plt.figure(figsize=(10, 8), dpi=400)
plt.box(0)
plt.margins(0)
width = 0.75
p1 = plt.barh(df['city'], df['eligiblefullpct'], width,
              color='#6688cc', label="Fully Vaccinated % of population > 12")
plt.legend(loc='best')
plt.legend().get_frame().set_linewidth(0.0)
plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.title('Cook County Full Vaccination Percentage (pop > 30k, age > 12)')
plt.grid(axis='x', linewidth=0.5)
# plt.xticks([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
for x, y in zip(df['city'], df['eligiblefullpct']):

    label = "{:0.1f}%".format(100*y)

    plt.annotate(label,  # this is the text
                 (y, x),  # this is the point to label
                 textcoords="offset points",  # how to position the text
                 xytext=(20, -3),  # distance from text to points (x,y)
                 ha='center')  # horizontal alignment can be left, right or center

plt.savefig('charts/Cook Municipal Full Vaccination (over 12 years) Ranking.png', bbox_inches='tight')
plt.close()