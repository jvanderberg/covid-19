import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv('regional_all.csv', header=[0,1], index_col=0)
df.index = pd.to_datetime(df.index)
plt.close()
plt.figure(figsize=(12, 5), dpi=400)
width = 0.75
p1 = plt.bar(df.index, df['deaths']['Illinois'], width, color='#3366cc')
plt.plot(df.index, df['deaths_7day']['Illinois'], color='#EE3333')
plt.ylabel("Daily Deaths")
plt.title('Illinois Daily Deaths')
# plt.xticks(np.arange(2000, taxyear, step=5))
plt.grid(axis='y', linewidth=0.5)
# plt.legend((p1[0]), ('Daily Deaths'))
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d')) 

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 

# Puts x-axis labels on an angle
plt.gca().xaxis.set_tick_params(rotation = 30)  
plt.savefig('IL Deaths.png')

