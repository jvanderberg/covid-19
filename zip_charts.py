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

df = pd.read_csv('zip_rollup_all.csv', header=[0], index_col=0, parse_dates=True)



#######################################################################################
# Positives/Positive testing %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(0)
plt.margins(0)
width = 0.75
p1 = plt.bar(df.index, df['count'], width, color='#6688cc', label="Daily Positives")
plt.plot(df.index, df['count_14day'], color='#EE3333', label="14 Day Average")
plt.ylabel("Daily Positives")
plt.legend(loc='best')
plt.legend().get_frame().set_linewidth(0.0)
current_value = df.tail(1)['count_14day'][0]
current_date = df.tail(1)['count_14day'].index[0]
plt.ylim(0)
plt.title('Oak Park Daily Positive cases - '+'{:%b %-d} - {:0.1f} cases per day'.format(current_date,current_value))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('Oak Park Positives.png', bbox_inches='tight')
plt.close()


#######################################################################################
# Positives by age group
#######################################################################################

age_groups = [{'group':'<20', 'color': 'tab:blue'}, {'group':'20-29', 'color': 'tab:orange'}, {'group':'30-39', 'color': 'tab:green'}, {'group': '40-49', 'color': 'tab:red'}, {'group': '50-59', 'color': 'tab:purple'}, {'group':'60-69', 'color': 'tab:brown'}, {'group':'70-79', 'color': 'tab:gray'}, {'group':'80+','color':'tab:cyan'} ]
age_groups.reverse()

plt.figure(figsize=(10, 5), dpi=400)
plt.box(0)
plt.margins(0)
x = df.index
y = []
for age in age_groups:
    y.append(df[age['group']+' count_14day'])
    #plt.plot(df.index, df[age['group']+' count_14day'], color=age['color'], linewidth=4, label=age['group'])

plt.stackplot(x,y, labels=[age['group'] for age in age_groups], alpha=0.75)
#plt.plot(df.index, df['count_14day'], color='black', label='All Ages', linewidth=4 )

plt.ylabel("Daily Positives")
plt.legend(loc='upper left', bbox_to_anchor=(1, 1)).get_frame().set_linewidth(0.0)

current_value = df.tail(1)['count_14day'][0]
current_date = df.tail(1)['count_14day'].index[0]

plt.title('Oak Park Cases by Age Group - '+'{:%b %-d} - 14 day average'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('Oak Park Positives by age.png', bbox_inches='tight')
plt.close()



#######################################################################################
# Tests by age group
#######################################################################################

age_groups = [{'group':'<20', 'color': 'tab:blue'}, {'group':'20-29', 'color': 'tab:orange'}, {'group':'30-39', 'color': 'tab:green'}, {'group': '40-49', 'color': 'tab:red'}, {'group': '50-59', 'color': 'tab:purple'}, {'group':'60-69', 'color': 'tab:brown'}, {'group':'70-79', 'color': 'tab:gray'}, {'group':'80+','color':'tab:cyan'} ]
age_groups.reverse()

plt.figure(figsize=(10, 5), dpi=400)
plt.box(0)
plt.margins(0)
x = df.index
y = []
for age in age_groups:
    y.append(df[age['group']+' tested_14day'])
    #plt.plot(df.index, df[age['group']+' count_14day'], color=age['color'], linewidth=4, label=age['group'])

plt.stackplot(x,y, labels=[age['group'] for age in age_groups], alpha=0.75)
#plt.plot(df.index, df['count_14day'], color='black', label='All Ages', linewidth=4 )

plt.ylabel("Daily Tests")
plt.legend(loc='upper left', bbox_to_anchor=(1, 1)).get_frame().set_linewidth(0.0)


plt.title('Oak Park Tests by Age Group - '+'{:%b %-d} - 14 day average'.format(current_date))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('Oak Park Tests by age.png', bbox_inches='tight')
plt.close()


#######################################################################################
# Positive testing %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
width = 0.75
plt.plot(df.index, df['percentage_14day'], color='#6688cc', label="14 Day Average")
plt.ylabel("% Positive")
plt.legend(loc='best')
plt.legend().get_frame().set_linewidth(0.0)
current_date = df.tail(1)['percentage_14day'].index[0]
current_value_percentage = df.tail(1)['percentage_14day'][0]

plt.title('Oak Park Daily Positive % - '+'{:%b %-d} - {:0.1f}% positive'.format(current_date, 100* current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0)) 
plt.ylim(0)
plt.savefig('Oak Park Positive Pct.png', bbox_inches='tight')
plt.close()

#######################################################################################
# Completed Test Report
#######################################################################################
plt.figure(1,figsize=(10, 5), dpi=400, clear=True)
width = 0.75
p1 = plt.bar(df.index, df['tested'], width, color='#6688cc', label="Tests Completed")
plt.plot(df.index, df['tested_14day'], color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Tests")
current_value = df.tail(1)['tested_14day'].round()[0]
current_date = df.tail(1)['tested_14day'].index[0]
plt.title('Oak Park Tests Completed - '+'{:%b %-d} - {:,} test per day'.format(current_date,int(current_value)))
plt.grid(axis='y', linewidth=0.5)
plt.ylim(0)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.box(False)
plt.legend()
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('Oak Park Testing.png', bbox_inches='tight')

#######################################################################################
# Positive testing % by zip
#######################################################################################
df = pd.read_csv('zip_detail_all.csv',  header=[0,1], index_col=0, parse_dates=True)

plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
width = 0.75
plt.plot(df.index, df['percentage_14day']['60301'], color='#6688cc', label="60301")
plt.plot(df.index, df['percentage_14day']['60302'], color='#EE3333', label="60302")
plt.plot(df.index, df['percentage_14day']['60304'], color='#33EE33', label="60304")
plt.ylabel("% Positive")
plt.legend(loc='best')
plt.legend().get_frame().set_linewidth(0.0)

current_date = df.tail(1)['percentage_14day']['60301'].index[0]
current_value_60301 = df.tail(1)['percentage_14day']['60301'][0]
current_value_60302 = df.tail(1)['percentage_14day']['60302'][0]
current_value_60304 = df.tail(1)['percentage_14day']['60304'][0]

plt.title('Oak Park Daily Positive % - '+'{:%b %-d} - 60301: {:0.1f}%  60302: {:0.1f}%  60304: {:0.1f}%'.format(current_date, 100* current_value_60301, 100* current_value_60302, 100* current_value_60304))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0)) 
plt.ylim(0)
plt.savefig('Oak Park Positive Pct by Zip.png', bbox_inches='tight')
plt.close()

