import json
import datetime
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib
import scipy.stats as stats

matplotlib.rcParams['text.color'] = '#555555'
matplotlib.rcParams['axes.labelcolor'] = '#555555'
matplotlib.rcParams['xtick.color'] = '#555555'
matplotlib.rcParams['ytick.color'] = '#555555'
startdate = datetime.datetime(2020, 8, 15)
df = pd.read_csv('us_daily.csv', index_col=0, parse_dates=True)

pos = df['positiveIncrease_7day']/df['totalTestResultsIncrease_7day']

df = pd.DataFrame({'deaths': df['deathIncrease'],
                   'cases': df['positiveIncrease'], 'tests': df['totalTestResultsIncrease']})

df = df[df.index > startdate]
#df = df[df.index < datetime.datetime(2020, 9, 15)]
df = df.rolling(window=7, center=True).mean()
df['percentage'] = df['cases'] / df['tests']
lag_correlations = np.zeros(80)
for i in range(0, 30):
    shifted = df['percentage'].shift(periods=i)
    corr = df['deaths'].corr(shifted)
    print(str(i) + ' ' + str(corr))
    lag_correlations[i] = corr

max_corr_lag = np.argmax(lag_correlations)
# max_corr_lag =
future_index = pd.date_range(
    df.tail(1).index[0]+datetime.timedelta(days=1), periods=max_corr_lag)
future = pd.DataFrame(index=future_index, columns=df.columns)
cfr = pd.concat((df, future))
cfr['percentage_lagged'] = cfr['percentage'].shift(periods=max_corr_lag)

clean = cfr.dropna()
slope, intercept, r_value, p_value, std_err = stats.linregress(
    clean['percentage_lagged'], clean['deaths'])
# fit = np.polyfit(clean['percentage_lagged'], y=clean['deaths'], deg=1, full=True)

cfr['fit'] = slope*cfr['percentage_lagged'] + intercept
cfr.to_csv('us_death_projections.csv')
#######################################################################################
# Deaths report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75
plt.scatter(cfr['percentage_lagged'], cfr['deaths'], c='#EE3333')
plt.plot(cfr['percentage_lagged'], cfr['fit'],
         label='Model Slope {:0.1f} deaths/% R² {:0.3f}'.format(slope/100, r_value**2))
plt.ylabel("Daily Deaths")
plt.xlabel("Lagged Case Positivity")
plt.title('Deaths vs {:0.0f} day lagged Case Positivity'.format(max_corr_lag))
plt.grid(axis='y', linewidth=0.5)
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/US Correlation.png')


#######################################################################################
# Deaths report
#######################################################################################
plt.close()
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75
plt.plot(cfr.index, cfr['deaths'], color='#EE3333', label="Deaths")
plt.plot(cfr.index, cfr['fit'], color='#AA33AA', label="Fit/Projection")
plt.ylabel("Daily Deaths")
plt.title('US Daily Deaths Projection')
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/US Deaths Projection.png')


# for lag in range(1,40):
#     future_index = pd.date_range(df.tail(1).index[0]+datetime.timedelta(days=1), periods=lag)
#     future = pd.DataFrame(index=future_index,columns=df.columns)
#     cfr = pd.concat((df,future))
#     cfr['percentage_lagged'] = cfr['percentage'].shift(periods=lag)
#     clean = cfr.dropna()
#     slope, intercept, r_value, p_value, std_err = stats.linregress(clean['percentage_lagged'], clean['deaths'])
#     # fit = np.polyfit(clean['percentage_lagged'], y=clean['deaths'], deg=1, full=True)

#     cfr['fit'] = slope*cfr['percentage_lagged'] + intercept
#     plt.close()
#     plt.figure(1,figsize=(10, 5), dpi=400)
#     width = 0.75
#     plt.plot(cfr.index, cfr['deaths'], color='#EE3333', label="Deaths", linewidth=3)
#     plt.plot(cfr.index, cfr['fit'], color='#AA33AA', label="Fit/Projection", linewidth=3)
#     plt.ylabel("Daily Deaths")
#     plt.title('US Daily Deaths Projection - '+str(lag)+' day lag of Case Positivity %')
#     plt.grid(axis='y', linewidth=0.5)
#     # Format the date into months & days
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

#     # Change the tick interval
#     plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
#     plt.box(False)
#     plt.legend().get_frame().set_linewidth(0.0)
#     plt.margins(0)
#     print('Lag '+str(lag)+' day animation frame')
#     plt.savefig('charts/US Deaths '+str(lag)+' day lag Projection.png')
