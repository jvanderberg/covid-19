import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib

df = pd.read_csv('state_first_second_wave.csv', index_col=0, parse_dates=True)

#######################################################################################
# Deaths Per Million First Wave vs Second
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)
plt.plot(df.index, df['deaths_per_millionfirst'], color='#6688cc', label="First Wave")
plt.plot(df.index, df['deaths_per_millionsecond'], color='#EE3333', label="Second Wave")
plt.ylabel("Deaths Per Million")
plt.ylim(0)
plt.legend()

plt.title('US Death Rates First Wave vs Second Wave')
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

plt.savefig('US Death Waves.png', bbox_inches='tight')
plt.close()

df = pd.read_csv('state_daily.csv', header=[0,1], index_col=0)

#######################################################################################
# Deaths Per Million First Wave vs Second
#######################################################################################
worst = df.tail(1)['worst_date'].transpose().reset_index().iloc[:,1]
states = df.tail(1)['worst_date'].transpose().reset_index().iloc[:,0]
sort_df = pd.DataFrame({'state': states, 'date': worst})
sort_df = sort_df.set_index('date')
sort_df.index = pd.to_datetime(sort_df.index)
sort_df = sort_df.sort_index()

items = sort_df['state'].values

length = len(items)
cols = 5
rows = int(np.ceil(length/cols))
plt.close()
plt.figure(1, dpi=400, clear=True)
f, ax = plt.subplots(rows,cols, sharey=True)


plt.rc('font', size=22)          # controls default text sizes
for row in range(0,rows):
    for col in range(0,cols):
        loc = row*cols+col
        if (loc <= length-1):
            item = items[loc]
            print(loc, item)
            current_value = df.tail(1)['deaths_per_million'][item][0]

            ax[row][col].plot(df.index, df['deaths_per_million'][item],linewidth=4, color='#6688cc')
            ax[row][col].set_title(item)
            ax[row][col].grid(axis='y', linewidth=0.5)
            ax[row][col].set_ylim(0,40)
            ax[row][col].tick_params(axis='x', labelsize=20)
            ax[row][col].tick_params(axis='y', labelsize=20)

            ax[row][col].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 
            ax[row][col].xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
 
print('Setting height...')
f.set_figheight(8* rows)
f.set_figwidth(8*cols)
print('Setting layout...')
f.tight_layout(pad=8, w_pad=1, h_pad=2)
f.suptitle('Deaths Per Million by State - 14 Day Average - Sorted by Date of Peak', fontsize=40)
# Format the date into months & days
print('Formatting axes...')
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
#plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
#plt.box(False)
print('Saving...')
plt.savefig('State Deaths.png', bbox_inches='tight')