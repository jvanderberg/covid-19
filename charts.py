import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv('regional_all.csv', header=[0,1], index_col=0)
df.index = pd.to_datetime(df.index)
plt.figure(1,figsize=(10, 5), dpi=400)
width = 0.75
p1 = plt.bar(df.index, df['deaths']['Illinois'], width, color='#6688cc', label="Daily Deaths")
plt.plot(df.index, df['deaths_7day']['Illinois'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Deaths")
current_value = df.tail(1)['deaths_7day']['Illinois'].round()[0]
current_date = df.tail(1)['deaths_7day']['Illinois'].index[0]
plt.title('Illinois Daily Deaths - '+'{:%b %-d} - {:0.0f} deaths per day'.format(current_date,current_value))
# plt.xticks(np.arange(2000, taxyear, step=5))
plt.grid(axis='y', linewidth=0.5)
# plt.legend((p1[0]), ('Daily Deaths'))
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
# Puts x-axis labels on an angle
#plt.gca().xaxis.set_tick_params(rotation = 30)  
plt.box(False)
plt.legend()
plt.margins(0)
plt.savefig('IL Deaths.png', bbox_inches='tight')

plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)

#fig, ax1 = plt.subplots()
p1 = plt.bar(df.index, df['count']['Illinois'], width, color='#6688cc', label="Daily Positives")
plt.plot(df.index, df['count_7day']['Illinois'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Positives")
plt.legend(loc=9).set_zorder(10)

ax2 = plt.twinx()
ax2.plot(df.index, df['percentage_7day']['Illinois'], color='#cca80a', label="% Positive", linewidth=3)
ax2.set_ylim(0)
ax2.set_ylabel("% Positive")
ax2.margins(0)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.legend(loc='best').set_zorder(10)
current_value = df.tail(1)['count_7day']['Illinois'].round()[0]
current_date = df.tail(1)['count_7day']['Illinois'].index[0]
current_value_percentage = df.tail(1)['percentage_7day']['Illinois'][0]

plt.title('Illinois Daily Positive cases - '+'{:%b %-d} - {:0.0f} cases per day - {:0.1f}% positive'.format(current_date,current_value, 100* current_value_percentage))
# plt.xticks(np.arange(2000, taxyear, step=5))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('IL Testing.png', bbox_inches='tight')

