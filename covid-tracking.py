from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime
import sys
import pytz

"""Federal data combiner tool. Downloads federal testing, hospitalization, and case/death data and combines it
into unified state-level output.

This script outputs a csv file named federal-covid-data-DATE.csv and is intended to be run in the Google Colab
environment, but passing the 'STDOUT' argument will output to STDOUT instead for command-line use.

Note: We at The COVID Tracking Project will not be maintaining this script in the event that the federal data pages
change in impactful ways. This is simply a set of instructions for interested data users.

Changelog:
2021-03-15: Initial release
"""

HHS_TESTING_URL = "https://beta.healthdata.gov/api/views/j8mb-icvb/rows.csv?accessType=DOWNLOAD"
HHS_HOSPITALIZATION_URL = "https://beta.healthdata.gov/api/views/g62h-syeh/rows.csv?accessType=DOWNLOAD"
CDC_CASE_DEATH_URL = "https://data.cdc.gov/api/views/9mfq-cb36/rows.csv?accessType=DOWNLOAD"

COMBINE_NY_NYC = True


def get_hospitalization_dailies():
    """build a dataframe containing the combination of several days of recent HHS hospitalization daily data"""
    csv_urls = get_hospitalization_csv_urls()
    data_frames = []

    for url in csv_urls:
        data = pd.read_csv(url, parse_dates=['reporting_cutoff_start'])
        # set each daily file's date to the reporting_cutoff_start date + 4 days
        data['date'] = data['reporting_cutoff_start'] + pd.DateOffset(days=4)
        data['date'] = data['date'].dt.date
        data_frames.append(data)
    hospitalization_dailies = pd.concat(data_frames)
    return hospitalization_dailies


def parse_dates(date_col):
    if date_col.str.contains(":").any():
        return pd.to_datetime(date_col, format='%m/%d/%Y %H:%M:%S %p').dt.date
    else:
        return pd.to_datetime(date_col, format='%Y-%m-%d').dt.date


# download and parse all three data files
[testing, hospitalization, case_death] = [pd.read_csv(url) for url in
                                          [HHS_TESTING_URL, HHS_HOSPITALIZATION_URL, CDC_CASE_DEATH_URL]]

# testing data comes out with one row per state/date/outcome combination.
# unpack that and squash it into one row per state/date only
testing = testing.set_index(
    ['state', 'date', 'overall_outcome']).unstack(level=-1)
testing = testing[['new_results_reported', 'total_results_reported']]
testing.columns = ['_'.join(tup).rstrip('_') for tup in testing.columns.values]
testing = testing.reset_index()
# allow for a choice of inconsistent datetime formats
testing['date'] = parse_dates(testing['date'])

# the HHS hospitalization time series is only updated weekly. To compensate, we download the latest daily data
# and merge it on top of the weekly data, taking only the most recent values for a given state/date
hospitalization['date'] = parse_dates(hospitalization['date'])
# hospitalization_dailies = get_hospitalization_dailies()
# we want to use the HHS weekly time series up until its last day, then fill in the rest of the data from the daily
# files. we overwrite the last day of the time series with the dailies because the dailies come out after the weekly
# hospitalization_dailies = hospitalization_dailies[hospitalization_dailies['date']
#                                                  >= hospitalization['date'].max()]
hospitalization.set_index(['state', 'date'])
# hospitalization = hospitalization.merge(hospitalization_dailies, how='outer')
# the keep='last' here keeps just the daily data when both duplicate weekly and daily data exist
hospitalization = hospitalization.drop_duplicates(
    subset=['date', 'state'], keep='last', ignore_index=True)
# select a subset of columns to include in the output
hospitalization = hospitalization[[
    'state',
    'date',
    'inpatient_beds_used_covid',
    'total_adult_patients_hospitalized_confirmed_and_suspected_covid',
    'total_adult_patients_hospitalized_confirmed_covid',
    'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid',
    'total_pediatric_patients_hospitalized_confirmed_covid',
    'staffed_icu_adult_patients_confirmed_and_suspected_covid',
    'staffed_icu_adult_patients_confirmed_covid',
    'previous_day_admission_adult_covid_confirmed',
    'previous_day_admission_adult_covid_suspected',
    'previous_day_admission_pediatric_covid_confirmed',
    'previous_day_admission_pediatric_covid_suspected',
    'inpatient_beds_used_covid_coverage',
    'total_adult_patients_hospitalized_confirmed_and_suspected_covid_coverage',
    'staffed_icu_adult_patients_confirmed_and_suspected_covid_coverage',
    'previous_day_admission_adult_covid_confirmed_coverage']]
# HHS hospitalization data gets better on and after 7/15/20
hospitalization = hospitalization[hospitalization['date'] >= datetime.date(
    year=2020, month=7, day=15)]

# case/death data: pick a subset of columns and prepare to merge
#case_death = case_death[
#    ['submission_date', 'state', 'tot_cases', 'conf_cases', 'prob_cases', 'new_case', 'pnew_case', 'tot_death',
#     'conf_death', 'prob_death', 'new_death', 'pnew_death']]
case_death = case_death.rename(columns={'submission_date': 'date'})
# sum NY and NYC case/death data into one row
if COMBINE_NY_NYC:
    # set all NYC rows to NY, group and sum the NY rows, and combine with the rest of the rows
    case_death.loc[case_death['state'] == 'NYC', ['state']] = 'NY'
    NY_combined = case_death[case_death['state']
                             == 'NY'].groupby(["date", "state"]).sum()
    case_death = NY_combined.reset_index().append(
        case_death[case_death['state'] != 'NY'])

# merge all the dataframes together into one big combination
combined = pd.merge(left=testing, right=hospitalization,
                    on=['state', 'date'], how='outer')

case_death['date'] = pd.to_datetime(case_death['date'], format='%m/%d/%Y')
combined['date'] = pd.to_datetime(combined['date'], format='%Y-%m-%d')

combined = combined.merge(case_death, on=['state', 'date'], how='outer')

combined.sort_values(by=['date', 'state'], inplace=True, ignore_index=True)
combined.to_csv('covid.csv', index=False)

# and output the data
new_combined = pd.DataFrame(
    {'date': combined['date'], 'state': combined['state'], 'hospitalized': combined['inpatient_beds_used_covid'], 'deathIncrease': combined['new_death'], 'totalTestResultsIncrease': (combined['new_results_reported_Inconclusive'] + combined['new_results_reported_Negative']+combined['new_results_reported_Positive']), 'positiveIncrease': combined['new_case']+ combined['pnew_case']})
new_combined.to_csv('covid-tracking.csv', index=False)

# tell Google Colab to have the user download the output
# or do nothing if we're not in a Colab environment
try:
    from google.colab import files
    files.download(outfile_name)
except ModuleNotFoundError:
    pass
