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

df = pd.read_csv('regional_hospitalization.csv', header=[
                 0, 1], index_col=0, parse_dates=True)
df2 = pd.read_csv('state_hospitalization.csv', index_col=1, parse_dates=True)
df = df[df.index > datetime.datetime(2020, 6, 12)]
df['icu'] = df['icu'].rolling(window=7).mean()
df['beds'] = df['beds'].rolling(window=7).mean()
df2 = df2[df2.index > datetime.datetime(2020, 6, 12)]
df2['IL_icu'] = df2['ICUOpenBeds_7day']/df2['ICUBeds_7day']
df2['IL_beds'] = df2['TotalOpenBeds_7day']/df2['TotalBeds_7day']
df = df.join(df2['IL_icu'])
df = df.join(df2['IL_beds'])


#######################################################################################
# ICU/Surg
#######################################################################################
items = [
    ['Chicago', 'Illinois', 'Suburban Cook', 'North Suburban'],
    ['West Suburban', 'South Suburban', 'North', 'North-Central'],
    ['East-Central', 'West-Central', 'Metro East', 'Southern']
]
plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3, 4, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020, 6, 11)]
for row in range(0, 3):
    for col in range(0, 4):
        item = items[row][col]
        if (item != 'Illinois'):
            current_value_icu = df.tail(1)[('icu', item)][0]
            current_value_beds = df.tail(1)[('beds', item)][0]
        else:
            current_value_icu = df.tail(1)['IL_icu'][0]
            current_value_beds = df.tail(1)['IL_beds'][0]

        if (item != 'Illinois'):
            ax[row][col].plot(june_plus.index, june_plus[('icu', item)],
                              linewidth=3, color='#6688cc', label='ICU Beds')
            ax[row][col].plot(june_plus.index, june_plus[('beds', item)],
                              linewidth=3, color='#cc6688', label='Hosp. Beds')
        else:
            ax[row][col].plot(june_plus.index, june_plus['IL_icu'],
                              linewidth=3, color='#6688cc', label='ICU Beds')
            ax[row][col].plot(june_plus.index, june_plus['IL_beds'],
                              linewidth=3, color='#cc6688', label='Hosp. Beds')

        ax[row][col].set_title(item + '\nICU {:0.1f}% - Beds {:0.1f}%'.format(
            100*current_value_icu, 100*current_value_beds))
        ax[row][col].grid(axis='y', linewidth=0.5)
        ax[row][col].set_ylim(0.2, 0.6)
        ax[row][col].spines["top"].set_visible(False)
        ax[row][col].spines["right"].set_visible(False)
        ax[row][col].spines["left"].set_visible(False)
        ax[row][col].spines["bottom"].set_visible(False)
        ax[row][col].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

ax[0][0].legend()

f.set_figheight(8)
f.set_figwidth(16)
f.tight_layout(pad=4, w_pad=-0.2, h_pad=3)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)

# plt.margins(0)
f.suptitle('Illinois Regional ICU and Hospital Bed % Available', fontsize=20)

plt.savefig('charts/Region ICU.png', dpi=400)


df = pd.read_csv('regional_all.csv', header=[0, 1], index_col=0)
df.index = pd.to_datetime(df.index)

#######################################################################################
# Deaths report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400)
width = 0.75
p1 = plt.bar(df.index, df['deaths']['Illinois'],
             width, color='#6688cc', label="Daily Deaths")
plt.plot(df.index, df['deaths_7day']['Illinois'],
         color='#EE3333', label="7 Day Average")
plt.ylabel("Daily Deaths")
current_value = df.tail(1)['deaths_7day']['Illinois'].round()[0]
current_date = df.tail(1)['deaths_7day']['Illinois'].index[0]
plt.title('Illinois Daily Deaths - ' +
          '{:%b %-d} - {:0.0f} deaths per day'.format(current_date, current_value))
plt.grid(axis='y', linewidth=0.5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/IL Deaths.png', bbox_inches='tight')


#######################################################################################
# Positives Cases
####################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)

p1 = plt.bar(df.index, df['count']['Illinois'], width,
             color='#6688cc', label="Daily Positives")
plt.plot(df.index, df['count_7day']['Illinois'],
         color='#EE3333', label="7 Day Average", linewidth=3)
plt.ylabel("Daily Positives")
plt.legend(loc=9).get_frame().set_linewidth(0.0)

current_value = df.tail(1)['count_7day']['Illinois'].round()[0]
current_date = df.tail(1)['count_7day']['Illinois'].index[0]
current_value_percentage = df.tail(1)['percentage_7day']['Illinois'][0]

plt.title('Illinois Daily Positive cases - '+'{:%b %-d} - {:,} cases per day - {:0.1f}% positive'.format(
    current_date, int(current_value), 100 * current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

plt.savefig('charts/IL Positives.png', bbox_inches='tight')
plt.close()


#######################################################################################
# Positive testing %
#######################################################################################
plt.figure(figsize=(10, 5), dpi=400)
plt.box(on=None)
plt.margins(0)

plt.plot(df.index, df['percentage_7day']['Illinois'],
         color='#EE3333', label="7 Day Average", linewidth=3)
plt.ylabel("Daily Positives")
plt.legend(loc=9).get_frame().set_linewidth(0.0)


plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
current_value = df.tail(1)['count_7day']['Illinois'].round()[0]
current_date = df.tail(1)['count_7day']['Illinois'].index[0]
current_value_percentage = df.tail(1)['percentage_7day']['Illinois'][0]
plt.ylim(0)
plt.title('Illinois Daily Positive % - '+'{:%b %-d} - {:,} cases per day - {:0.1f}% positive'.format(
    current_date, int(current_value), 100 * current_value_percentage))
plt.grid(axis='y', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

plt.savefig('charts/IL Positive Pct.png', bbox_inches='tight')
plt.close()

#######################################################################################
# Completed Test Report
#######################################################################################
plt.figure(1, figsize=(10, 5), dpi=400, clear=True)
width = 0.75
p1 = plt.bar(df.index, df['tested']['Illinois'], width,
             color='#6688cc', label="Tests Completed")
plt.plot(df.index, df['tested_7day']['Illinois'],
         color='#EE3333', label="7 Day Average", linewidth=3)
plt.ylabel("Daily Tests")
current_value = df.tail(1)['tested_7day']['Illinois'].round()[0]
current_date = df.tail(1)['tested_7day']['Illinois'].index[0]
plt.title('Illinois Tests Completed - ' +
          '{:%b %-d} - {:,} test per day'.format(current_date, int(current_value)))
plt.grid(axis='y', linewidth=0.5)
plt.ylim(0, 120000)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)
plt.legend().get_frame().set_linewidth(0.0)
plt.margins(0)
plt.savefig('charts/IL Testing.png', bbox_inches='tight')

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
f, ax = plt.subplots(3, 4, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020, 5, 31)]
for row in range(0, 3):
    for col in range(0, 4):
        item = items[row][col]
        current_value = df.tail(1)['percentage_7day'][item][0]

        ax[row][col].plot(june_plus.index, june_plus['percentage_7day']
                          [item], linewidth=3, color='#6688cc')
        ax[row][col].set_title(item + ' - {:0.1f}%'.format(100*current_value))
        ax[row][col].grid(axis='y', linewidth=0.5)
        ax[row][col].set_ylim(0, .2)
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

# plt.margins(0)
f.suptitle('Illinois Regional % Positive - 7 Day Average', fontsize=20)

plt.savefig('charts/Region Percentage.png', dpi=400)

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
f, ax = plt.subplots(3, 4, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020, 5, 31)]
for row in range(0, 3):
    for col in range(0, 4):
        item = items[row][col]
        current_value = df.tail(1)['deaths_per_million_7day'][item][0]

        ax[row][col].plot(june_plus.index, june_plus['deaths_per_million_7day']
                          [item], linewidth=3, color='#6688cc')
        ax[row][col].set_title(item + ' - {:0.1f}'.format(current_value))
        ax[row][col].grid(axis='y', linewidth=0.5)
        ax[row][col].set_ylim(0, 10)
        ax[row][col].spines["top"].set_visible(False)
        ax[row][col].spines["right"].set_visible(False)
        ax[row][col].spines["left"].set_visible(False)
        ax[row][col].spines["bottom"].set_visible(False)


f.set_figheight(8)
f.set_figwidth(16)
f.tight_layout(pad=4, w_pad=-0.2, h_pad=3)
f.suptitle(
    'Illinois Regional Daily Death Rates Per Million - 7 Day Average', fontsize=20)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)

# plt.margins(0)
plt.savefig('charts/Region Deaths per Million.png', dpi=400)

#######################################################################################
# Regional Cases Per Million
#######################################################################################
items = [
    ['City of Chicago', 'Illinois', 'Suburban Cook', 'North Suburban'],
    ['West Suburban', 'South Suburban', 'North', 'North-Central'],
    ['East-Central', 'West-Central', 'Metro East', 'Southern']
]
plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3, 4, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020, 5, 31)]
for row in range(0, 3):
    for col in range(0, 4):
        item = items[row][col]
        current_value = df.tail(1)['count_per_million_7day'][item][0]

        ax[row][col].plot(june_plus.index, june_plus['count_per_million_7day']
                          [item], linewidth=3, color='#6688cc')
        ax[row][col].set_title(item + ' - {:0.1f}'.format(current_value))
        ax[row][col].grid(axis='y', linewidth=0.5)
        ax[row][col].set_ylim(0, 1400)
        ax[row][col].spines["top"].set_visible(False)
        ax[row][col].spines["right"].set_visible(False)
        ax[row][col].spines["left"].set_visible(False)
        ax[row][col].spines["bottom"].set_visible(False)


f.set_figheight(8)
f.set_figwidth(16)
f.tight_layout(pad=4, w_pad=-0.2, h_pad=3)
f.suptitle(
    'Illinois Regional Daily Positive Cases Per Million - 7 Day Average', fontsize=20)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)

# plt.margins(0)
plt.savefig('charts/Region Cases per Million.png', dpi=400)

#######################################################################################
# State Hospitalization
#######################################################################################

df = pd.read_csv('state_hospitalization.csv', index_col=1, parse_dates=True)
df = df[df.index > datetime.datetime(2020, 3, 1)]
plt.figure()
f, ax = plt.subplots(2)
plt.box(on=None)
ax[0].plot(df.index, df['VentilatorInUseCOVID_7day'],
           color='#6688cc', label="Ventilator 7day", linewidth=3)
ax[0].plot(df.index, df['ICUInUseBedsCOVID_7day'],
           color='#EE3333', label="ICU 7day", linewidth=3)
ax[1].plot(df.index, df['TotalInUseBedsCOVID_7day'],
           color='#cca80a', label="COVID Patients 7day", linewidth=3)

ax[0].set_ylim(0)
ax[1].set_ylim(0)


ax[0].legend().get_frame().set_linewidth(0.0)
ax[1].legend().get_frame().set_linewidth(0.0)

vent_value = df.tail(1)['VentilatorInUseCOVID_7day'].values[0]
vent_pct = vent_value / df.tail(1)['VentilatorCapacity_7day'].values[0]
icu_value = df.tail(1)['ICUInUseBedsCOVID_7day'].values[0]
icu_pct = icu_value / df.tail(1)['ICUBeds_7day'].values[0]
bed_value = df.tail(1)['TotalInUseBedsCOVID_7day'].values[0]
bed_pct = bed_value / df.tail(1)['TotalBeds_7day'].values[0]
current_date = df.tail(1)['VentilatorInUseCOVID_7day'].index[0]
ax[0].set_title('Hospitalization - '+'{:%b %-d} - {:,} ICU Beds - {:,} Ventilators'.format(
    current_date, int(icu_value), int(vent_value), fontsize=16))
ax[1].set_title('Hospitalization - '+'{:%b %-d} - {:,} Total COVID Patients '.format(
    current_date, int(bed_value)), fontsize=16)
ax[0].grid(axis='y', linewidth=0.5)
ax[1].grid(axis='y', linewidth=0.5)
ax[0].spines["top"].set_visible(False)
ax[0].spines["right"].set_visible(False)
ax[0].spines["left"].set_visible(False)
ax[0].spines["bottom"].set_visible(False)
ax[1].spines["top"].set_visible(False)
ax[1].spines["right"].set_visible(False)
ax[1].spines["left"].set_visible(False)
ax[1].spines["bottom"].set_visible(False)
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=1))

f.set_figheight(10)
f.set_figwidth(10)
f.tight_layout(pad=1, w_pad=3, h_pad=5)
plt.savefig('charts/IL Hospitalization.png', dpi=200)
plt.close()


df = pd.read_csv('regional_north_south.csv', header=[
    0, 1], index_col=0, parse_dates=True)

#######################################################################################
# North/South Positive %
#######################################################################################
items = ['Illinois', 'North', 'South']

plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3, sharex=True, sharey=True)
june_plus = df[df.index > datetime.datetime(2020, 5, 31)]
for col in range(0, 3):
    item = items[col]
    current_value = df.tail(1)['percentage_7day'][item][0]

    ax[col].plot(june_plus.index, june_plus['percentage_7day']
                 [item], color='#6688cc', linewidth=3)
    ax[col].set_title(
        item + ' - {:0.1f}%'.format(100*current_value), fontsize=18)
    ax[col].grid(axis='y', linewidth=0.5)
    ax[col].set_ylim(0, .16)
    ax[col].spines["top"].set_visible(False)
    ax[col].spines["right"].set_visible(False)
    ax[col].spines["left"].set_visible(False)
    ax[col].spines["bottom"].set_visible(False)
    ax[col].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax[col].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax[col].xaxis.set_major_locator(mdates.MonthLocator(interval=1))

f.set_figheight(16)
f.set_figwidth(8)
f.tight_layout(pad=6, w_pad=1, h_pad=5)
# Format the date into months & days
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

# Change the tick interval
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.box(False)

# plt.margins(0)
f.suptitle('Illinois North/South % Positive - 7 Day Average', fontsize=18)

plt.savefig('charts/North-South Percentage.png', dpi=400)

#######################################################################################
# North/South Deaths Per Million
#######################################################################################

plt.close()
plt.figure(1, dpi=800, clear=True)
f, ax = plt.subplots(3, sharex=False, sharey=True)
june_plus = df[df.index > datetime.datetime(2020, 4, 30)]
for col in range(0, 3):
    item = items[col]
    current_value = df.tail(1)['deaths_per_million_7day'][item][0]

    ax[col].plot(june_plus.index, june_plus['deaths_per_million_7day']
                 [item], color='#6688cc', linewidth=3)
    ax[col].set_title(item + ' - {:0.1f}'.format(current_value), fontsize=18)
    ax[col].grid(axis='y', linewidth=0.5)
    ax[col].set_ylim(0, 10)
    ax[col].spines["top"].set_visible(False)
    ax[col].spines["right"].set_visible(False)
    ax[col].spines["left"].set_visible(False)
    ax[col].spines["bottom"].set_visible(False)
    ax[col].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax[col].xaxis.set_major_locator(mdates.MonthLocator(interval=1))


f.set_figheight(16)
f.set_figwidth(8)
f.tight_layout(pad=6, w_pad=1, h_pad=5)
f.suptitle(
    'Illinois North/South Death Rates Per Million - 7 Day Average', fontsize=18)

plt.box(False)

# plt.margins(0)
plt.savefig('charts/North-South deaths per Million.png', dpi=200)
