# Add Parent Folder to System Path

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

####

import pandas as pd
import numpy as np

df_coal=pd.read_csv("../row_data/coal-prices.csv")
df_countries=pd.read_csv("../row_data/Countries_ISO3.csv")
df_countries=pd.read_csv("../row_data/Countries_ISO3.csv")

#### HISTORICAL ######

countries=df_countries['Country Name'].values
ISO3=np.unique(df_countries['ISO3'].values)
years=np.unique(df_coal['Year'].values)
coun_year=[]
for count in zip(countries,ISO3):
    for year in years:
        coun_year.append([count[0],count[1],year])
df_historical_out = pd.DataFrame(coun_year, columns=['Country','ISO3', 'Year'])

#df_coal=pd.read_csv("../row_data/coal-prices.csv")
df_coal.set_index("Year", inplace = True)
# Using the operator .loc[]
# to select single row
average_prices=[]

for y in years:
    yp = np.average(df_coal.loc[y]['Coal - Prices'])
    average_prices.append(yp)

average_prices=np.array(average_prices)
prices=average_prices*1.346
p=[]
for i in countries:
    p=np.append(p,prices)
df_historical_out['cost_enfu_fuel_coal_usd_per_m3']=p
df_historical_out.to_csv('../input_to_sisepuede/historical/cost_enfu_fuel_coal_usd_per_m3.csv')

#### PROJECTED ######

#Prediction for the next years will be the last historical value
years2=years
prices2=prices
for y in np.arange(min(years2),2051,1):
    if y not in years2:
        years2=np.append(years2,y)
        prices2=np.append(prices2,prices2[-1])

coun_year2=[]
for count in zip(countries,ISO3):
    for y_p in zip(years2,prices2):
        coun_year2.append([count[0],count[1],y_p[0],y_p[1]])
coun_year2

df_projected_out = pd.DataFrame(coun_year2, columns=['Country','ISO3', 'Year','cost_enfu_fuel_coal_usd_per_m3'])
df_projected_out.to_csv('../input_to_sisepuede/projected/cost_enfu_fuel_coal_usd_per_m3.csv')
