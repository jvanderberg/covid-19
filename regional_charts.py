import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

df = pd.read_csv('regional_all.csv', header=[0,1], index_col=0)
df.index = pd.to_datetime(df.index)

#######################################################################################
# Deaths report
#######################################################################################
plt.figure(1,figsize=(10, 5), dpi=400)
width = 0.75
p1 = plt.bar(df.index, df['deaths']['Illinois'], width, color='#6688cc', label="Daily Deaths")
plt.plot(df.index, df['deaths_7day']['Illinois'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Deaths")
current_value = df.tail(1)['deaths_7day']['Illinois'].round()[0]
current_date = df.tail(1)['deaths_7day']['Illinois'].index[0]
plt.title('Illinois Daily Deaths - '+'{:%b %-d} - {:0.0f} deaths per day'.format(current_date,current_value))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)
plt.legend()
plt.margins(0)
plt.savefig('IL Deaths.png', bbox_inches='tight')


#######################################################################################
# Positives/Positive testing %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)

p1 = plt.bar(df.index, df['count']['Illinois'], width, color='#6688cc', label="Daily Positives")
plt.plot(df.index, df['count_7day']['Illinois'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Positives")
plt.legend(loc=9).set_zorder(10)

ax2 = plt.twinx()
ax2.plot(df.index, df['percentage_7day']['Illinois'], color='#cca80a', label="% Positive", linewidth=3)
ax2.set_ylim(0)
ax2.set_ylabel("% Positive")
ax2.margins(0)

ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.legend(loc='best').set_zorder(10)
current_value = df.tail(1)['count_7day']['Illinois'].round()[0]
current_date = df.tail(1)['count_7day']['Illinois'].index[0]
current_value_percentage = df.tail(1)['percentage_7day']['Illinois'][0]

plt.title('Illinois Daily Positive cases - '+'{:%b %-d} - {:,} cases per day - {:0.1f}% positive'.format(current_date,int(current_value), 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('IL Positives.png', bbox_inches='tight')
plt.close()


#######################################################################################
# Completed Test Report
#######################################################################################
plt.figure(1,figsize=(10, 5), dpi=400, clear=True)
width = 0.75
p1 = plt.bar(df.index, df['tested']['Illinois'], width, color='#6688cc', label="Tests Completed")
plt.plot(df.index, df['tested_7day']['Illinois'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Tests")
current_value = df.tail(1)['tested_7day']['Illinois'].round()[0]
current_date = df.tail(1)['tested_7day']['Illinois'].index[0]
plt.title('Illinois Tests Completed - '+'{:%b %-d} - {:,} test per day'.format(current_date,int(current_value)))
plt.grid(axis='y', linewidth=0.5)
plt.ylim(0,65000)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)
plt.legend()
plt.margins(0)
plt.savefig('IL Testing.png', bbox_inches='tight')

#######################################################################################
# Regional Positive %
#######################################################################################
items = [
    ['City of Chicago', 'Illinois', 'Suburban Cook', 'North Suburban'],
    ['West Suburban', 'South Suburban', 'North', 'North-Central'],
    ['East-Central', 'West-Central', 'Metro East', 'Southern']
]
plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3,4, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020,5,31)]
for row in range(0,3):
    for col in range(0,4):
        item = items[row][col]
        current_value = df.tail(1)['percentage_7day'][item][0]

        ax[row][col].plot(june_plus.index, june_plus['percentage_7day'][item], color='#6688cc')
        ax[row][col].set_title(item +' - {:0.1f}%'.format(100*current_value))
        ax[row][col].grid(axis='y', linewidth=0.5)
        ax[row][col].set_ylim(0,.12)
        ax[row][col].spines["top"].set_visible(False)
        ax[row][col].spines["right"].set_visible(False)
        ax[row][col].spines["left"].set_visible(False)
        ax[row][col].spines["bottom"].set_visible(False)
        ax[row][col].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))


f.set_figheight(8)
f.set_figwidth(16)
f.tight_layout(pad=4, w_pad=-0.2, h_pad=3)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0)) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)

#plt.margins(0)
f.suptitle('Illinois Regional % Positive - 7 Day Average', fontsize=20)

plt.savefig('Region Percentage.png', dpi=400)

#######################################################################################
# Regional Deaths Per Million
#######################################################################################
items = [
    ['City of Chicago', 'Illinois', 'Suburban Cook', 'North Suburban'],
    ['West Suburban', 'South Suburban', 'North', 'North-Central'],
    ['East-Central', 'West-Central', 'Metro East', 'Southern']
]
plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3,4, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020,5,31)]
for row in range(0,3):
    for col in range(0,4):
        item = items[row][col]
        current_value = df.tail(1)['deaths_per_million_7day'][item][0]

        ax[row][col].plot(june_plus.index, june_plus['deaths_per_million_7day'][item], color='#6688cc')
        ax[row][col].set_title(item +' - {:0.1f}'.format(current_value))
        ax[row][col].grid(axis='y', linewidth=0.5)
        ax[row][col].set_ylim(0,10)
        ax[row][col].spines["top"].set_visible(False)
        ax[row][col].spines["right"].set_visible(False)
        ax[row][col].spines["left"].set_visible(False)
        ax[row][col].spines["bottom"].set_visible(False)


f.set_figheight(8)
f.set_figwidth(16)
f.tight_layout(pad=4, w_pad=-0.2, h_pad=3)
f.suptitle('Illinois Regional Death Rates Per Million - 7 Day Average', fontsize=20)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)

#plt.margins(0)
plt.savefig('Region Deaths per Million.png', dpi=400)