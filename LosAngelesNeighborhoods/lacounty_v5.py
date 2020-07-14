#!/usr/bin/env python
# -*- coding: utf8 -*-

# # Webscraping from LA County COVID-19 Site and Creating Plot
# - Patty Jula, <pattyjula@gmail.com>
# 
# LA County Public Health has been providing daily counts of the number of cases and 
# rates Los Angeles County from COVID-19. This script provides a way to download the day's counts, 
# load to a database, in this case a CSV, and create a plot. 
# 
# Source: <http://publichealth.lacounty.gov/media/Coronavirus/locations.htm>
# ## Note:
# This type of webscraping is only available from sites that reveal their source code. 
# The best practice is to ask permission before scraping so an organization's servers 
# are not overloaded.
#
# The content of this repository is provided "as is" without warranty of any kind.
# The data is subject to change at anytime.
#
# Import Dependencies
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import datetime
import time

# Boilerplate code
url = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'
res = requests.get(url)
html_page = res.content

# Parse through the html
soup = BeautifulSoup(html_page, 'html.parser')
#print(soup.prettify())

# Load data to a Pandas dataframe
caser = 'case_rate'
cases = 'cases'
deaths = 'deaths'
deathr = 'death_rate'
# column names
column = ['location', cases, caser, deaths, deathr]

# data is an empty list
data = []
count = 0
table = soup.find("table", {"table table-striped table-bordered table-sm"})#.findAll('tr')
for element in table.findAll("tr"):
    count += 1
    if count > 29: # first 29 rows are not needed
        # find cells containing td
        cells = element.findAll("td")
        info = [cell.text for cell in cells] # get the cell text
        data.append(info) # append to data list
        time.sleep(1) # pause to avoid taxing servers
df_day = pd.DataFrame(data, columns= column,) # convert to dataframe

# handle empty cells, they are not read as NaN by default
# So NaN needs to be specified
df_day[caser].replace('', np.nan, inplace=True)
# now delete the NA cells
df_day.dropna(subset=[caser], inplace=True)

# Save as a CSV
df_day.to_csv("./data/county.csv", encoding='utf-8', index=False)
# Read that CSV

df_day = pd.read_csv('./data/county.csv', index_col=False)

# Data Wrangling steps

df_day = df_day[df_day['case_rate'] != '--'] # drop select records
# Focusing here on Los Angeles City neighborhoods
df_day=df_day[df_day['location'].apply(lambda x: x.startswith('Los Angeles -'))]
df_day.case_rate.astype(float)
df_day = df_day.sort_values(by='case_rate', ascending=False)

df_day.head()

# Add today's date to the dataframe

def today_date():
    '''
    utils:
    get the datetime of today
    '''
    date=datetime.datetime.now().date()
    date=pd.to_datetime(date)
    return date
df_day['Date'] = today_date()

# Explicitly convert Date field to date

df_day['Date'] = pd.to_datetime(df_day['Date']).dt.date
#df2['count'] = d2['count'].str.replace(',', '').astype(int)
df_day['location'] = df_day.location.str.replace('City of ', '')
df_day['location'] = df_day.location.str.replace('Los Angeles - ', '')
df_day['location'] = df_day.location.str.replace('Unincorporated - ', '')

df_day['location'] = df_day.location.str.upper()
df_day.head() 

df_day.to_csv("./data/nbhrd_day.csv", encoding='utf-8', index=False)

# Now let's deal with the existing database

# This existing database contains previous day's data

dfDB = pd.read_csv("./data/neighborhood_storage.csv", parse_dates=['Date'])#, dayfirst=True)
#dfDB.set_index('Date')
#dfDB.head()


# If current day's date is already in database, delete it

for index, row in dfDB.iterrows():
    #print(row['Date'])
    if row['Date'] == today_date():
        #print('Found')
        dfDB.drop(index, inplace=True)
    else:
        pass

# Then let's add the newly scraped data to the database
# with append
df= dfDB.append(df_day, ignore_index = True,sort=True)
df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y')

# Convert location field to upper
# so it can join with communities shapefile
df['location'] = df.location.str.upper()
# handle empty cells, they are not read as NaN by default
df['case_rate'].replace('', np.nan, inplace=True)
# now they can be deleted
df.dropna(subset=['case_rate'], inplace=True)
df['location'] = df['location'].str.rstrip('*')
df.to_csv("./data/neighborhood_storage.csv", encoding='utf-8', index=False)
df.to_excel("./data/neighborhood_storage.xlsx", index=False)
print(df.head())

'''
Join Data to shapefile
'''
dfday = pd.read_csv("./data/nbhrd_day.csv")# parse_dates=['Date'])#, dayfirst=True)
import geopandas
#url = "http://s3-us-west-2.amazonaws.com/boundaries.latimes.com/archive/1.0/boundary-set/la-county-neighborhoods-current.geojson"
gdf = geopandas.read_file("./data/LACity_communities.shp")
#gdf = geopandas.read_file(url)
gdf.plot()

gdfNew = gdf.merge(df_day, left_on='COMTY_NAME', right_on='location')#, how='inner')

# Data wrangling to get fields in proper format
gdfNew[["Date"]] = gdfNew[["Date"]].astype(str)
gdfNew[['case_rate']] = gdfNew[['case_rate']].astype(float) 
gdfNew[['cases']] = gdfNew[['cases']].astype(int) 
gdfNew[['death_rate']] = gdfNew[['death_rate']].astype(float) 
gdfNew[['deaths']] = gdfNew[['deaths']].astype(int) 

# Export to shapefile
gdfNew.to_file(driver = 'ESRI Shapefile', filename= './data/nghbrhd_data.shp')

