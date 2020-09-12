import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

df = pd.read_csv('us_daily.csv', index_col=0, parse_dates=True)

date_from = datetime.datetime(2020,4,1)
df = df[df.index >= date_from ]
#######################################################################################
# US National Deaths
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
plt.bar(df.index, df['deathIncrease'], width=0.75, color='#6688cc', label="Daily Deaths")
plt.plot(df.index, df['deathIncrease_7day'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Deaths")
plt.ylim(0)
plt.legend()

current_value = df.tail(1)['deathIncrease_7day'].round()[0]
current_date = df.tail(1)['deathIncrease_7day'].index[0]
current_value_percentage =(df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day']).tail(1)[0]

plt.title('US Daily Deaths - '+'{:%b %-d} - {:,} Deaths Avg / day - {:0.1f}% positive'.format(current_date,int(current_value), 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('US Death.png', bbox_inches='tight')
plt.close()

#######################################################################################
# US National Testing
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
plt.bar(df.index, df['totalTestResultsIncrease'], width=0.75, color='#6688cc', label="Daily Tests")
plt.plot(df.index, df['totalTestResultsIncrease_7day'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Tests Completed")
plt.ylim(0)
plt.legend()

current_value = df.tail(1)['totalTestResultsIncrease_7day'].round()[0]
current_date = df.tail(1)['totalTestResultsIncrease_7day'].index[0]
current_value_percentage =(df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day']).tail(1)[0]

plt.title('US Daily Tests Completed - '+'{:%b %-d} - {:,} Tests Avg / day - {:0.1f}% positive'.format(current_date,int(current_value), 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('US Tests.png', bbox_inches='tight')
plt.close()

######################################################################################
# US Positive Cases
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
plt.bar(df.index, df['positiveIncrease'], width=0.75, color='#6688cc', label="Daily Positive Cases")
plt.plot(df.index, df['positiveIncrease_7day'], color='#EE3333', label="7 Day Average")
plt.ylabel("Positive Cases")
plt.ylim(0)
plt.legend()

current_value = df.tail(1)['positiveIncrease_7day'].round()[0]
current_date = df.tail(1)['positiveIncrease_7day'].index[0]
current_value_percentage =(df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day']).tail(1)[0]

plt.title('US Daily Positive Cases - '+'{:%b %-d} - {:,} Cases Avg / day - {:0.1f}% positive'.format(current_date,int(current_value), 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('US Positive Cases.png', bbox_inches='tight')
plt.close()


######################################################################################
# US Positive %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
pos = df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day']
plt.plot(df.index, pos, color='#EE3333', label="7 Day Average")
plt.ylabel("Positive %")
plt.ylim(0)
plt.legend()

current_date = df.tail(1)['positiveIncrease_7day'].index[0]
current_value_percentage =(pos).tail(1)[0]

plt.title('US Daily Positive Percentage - '+'{:%b %-d} - {:0.1f}% positive'.format(current_date, 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0)) 

plt.savefig('US Positive Percentage.png', bbox_inches='tight')
plt.close()
