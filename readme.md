IL COVID-19 Resources

# Running the data collection scripts

1. python zipcode.py
2. python county.py
3. python national.py

# Running the chart generating scripts

1. python zip_charts.py
2. python regional_charts.py
3. python national_charts.py

# Script inventory

## zipcode.py
Pulls the latest zipcode based breakdown from the IDPH website @ https://www.dph.illinois.gov/sitefiles/COVIDZip.json?nocache=1, and generates the file mm-dd.json for the data of the file.  Each one of these files contains one day's worth of data.

It then reads all of the days into a data structure, interpolates missing days, filters to the OP zip codes and calculates 7 and 14 day averages.  It then generates 'zip_rolloup_all.csv' which has the three OP zips combined, and 'zip_detail_all.csv', which has the data broken out by zipcode.

## county.py

This pulls the latest data from https://www.dph.illinois.gov/sitefiles/COVIDHistoricalTestResults.json?nocache=5. This file is all of the county based data for all history. The code then uses 'regions.csv' to roll-up the county based data to the 11 IDPH COVID-19 regions. A 12th 'region' of Illinois is also included.

The script then removes some spurious data and calculates 7day and 14 day rolling averages, and writes those out to 'regional_all.csv'.

## national.py

This pulls the latest national aggregate data (no state detail) from https://api.covidtracking.com/v1/us/daily.csv. This file contains all of the historical data from the US. The script then generates 7 day rolling averages and writes the data to 'us_daily.csv'






