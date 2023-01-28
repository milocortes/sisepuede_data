import os 
import sys
import pandas as pd
import re


# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ))

## Load historical data
historical_path = os.path.join(sources_path,"transport_energy_Indicators.csv")
historical_data = pd.read_csv(historical_path)

## Get data frm 2010 to 2020
historical_data["Indicator"] = historical_data["Indicator"].apply(lambda x: re.sub(' +', ' ',x)[:-1])

historical_data = historical_data[(historical_data["Mode/vehicle type"]=="Freight trucks") & (historical_data["Indicator"]=="Fuel intensity (litres/100 vkm)")] 

historical_data = historical_data[historical_data["2010"]!=".."][["Country", "2010", "2015", "2016", "2017", "2018", "2019", "2020"]].replace("..",0).reset_index(drop = True)

historical_data.set_index("Country", inplace = True)

listo_to_df = []

for country in historical_data.index:
    acumula_registro = [country]
    for year in [2010] + list(range(2015, 2021)):
        if year == 2010:
            acumula_registro.extend([float(historical_data.loc[country, str(year)])]*5)
        else:
            valor_anio = float(historical_data.loc[country, str(year)])
            if valor_anio == 0.0:
                acumula_registro.append(acumula_registro[-1])
            else:
                acumula_registro.append(valor_anio)
    
    listo_to_df.append(tuple(acumula_registro))


road_heavy_freight = pd.DataFrame(listo_to_df, columns = ["Nation"] + list(range(2010, 2021)))

# Rename China
road_heavy_freight.loc[road_heavy_freight["Nation"]=="Hong Kong (China)","Nation"] = "China"

## Load ISO3 codes
iso3_code_path = os.path.join(sources_path,"iso3_countries.csv")

iso3_code = pd.read_csv(iso3_code_path)
iso3_code.dropna(inplace = True)

iso3_code = iso3_code[["Continent", "Name", "ISO 3"]]

iso3_code = iso3_code.rename(columns = {"Name":"Nation"}) 

road_heavy_freight = road_heavy_freight.merge(right = iso3_code, how = "inner", on = "Nation")

melt_road_heavy_freight = pd.melt(road_heavy_freight, id_vars = ["Nation", "Continent", "ISO 3"]).sort_values(by = ["Nation", "variable"]).reset_index(drop = True)

## Rename columns
var_sisepuede = "fuelefficiency_trns_road_heavy_freight_diesel_km_per_litre"

melt_road_heavy_freight = melt_road_heavy_freight.rename(columns = {"variable" : "Year", "value" : var_sisepuede, "ISO 3" : "iso_code3"})

continent_efficiency_val = melt_road_heavy_freight[["Continent", "Year", var_sisepuede]].groupby(["Continent","Year"]).mean().reset_index()

world_efficiency_val = continent_efficiency_val[["Year", var_sisepuede]].groupby("Year").mean().reset_index() 

## Build serie for each country

iso3_code = iso3_code.set_index("Nation")
acumula_partial_df = []

for country in iso3_code.index:
    if any(melt_road_heavy_freight.Nation.isin([country])):
        partial_country = melt_road_heavy_freight[melt_road_heavy_freight.Nation.isin([country])][["Nation", "iso_code3", "Year", var_sisepuede]] 
        acumula_partial_df.append(partial_country)
    elif  any(continent_efficiency_val["Continent"].isin([iso3_code.loc[country,"Continent"]])):
        year_value_country = continent_efficiency_val[continent_efficiency_val["Continent"].isin([iso3_code.loc[country,"Continent"]])][["Year", var_sisepuede]].reset_index(drop = True)
        nation_iso3_code_country = pd.DataFrame({"Nation" : [country]*len(range(2010, 2021)), "iso_code3" : [iso3_code.loc[country,"ISO 3"] ]* len(range(2010,2021))}) 
        partial_country = pd.concat([nation_iso3_code_country, year_value_country], axis = 1)
        acumula_partial_df.append(partial_country)

    else:
        year_value_country = world_efficiency_val.copy()
        nation_iso3_code_country = pd.DataFrame({"Nation" : [country]*len(range(2010, 2021)), "iso_code3" : [iso3_code.loc[country,"ISO 3"] ]* len(range(2010,2021))}) 
        partial_country = pd.concat([nation_iso3_code_country, year_value_country], axis = 1)
        acumula_partial_df.append(partial_country)

all_historical_df = pd.concat(acumula_partial_df, ignore_index = True)
all_historical_df[var_sisepuede] = all_historical_df[var_sisepuede].apply(lambda x: (x**(-1)*100))
save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

file_save_path_historical = os.path.join(save_path_historical, f"{var_sisepuede}.csv")

all_historical_df.to_csv(file_save_path_historical, index = False)

# Build and save to csv projected data
projected_acumula_partial_df = []

for country in iso3_code.index:
    last_value = all_historical_df.query(f'Nation == "{country}"')[var_sisepuede].tolist()[-1]
    last_year = all_historical_df.query(f'Nation == "{country}"')["Year"].tolist()[-1]

    time_period = range(last_year +1, 2051)
    
    partial_country = pd.DataFrame({"Nation" : [country]*len(time_period) ,
                  "iso_code3" : [iso3_code.loc[country, "ISO 3"]]*len(time_period),
                  "Year" : time_period, 
                  var_sisepuede : [last_value]*len(time_period)})
    
    projected_acumula_partial_df.append(partial_country)

all_projected_df = pd.concat(projected_acumula_partial_df, ignore_index = True)


save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

file_save_path_projected = os.path.join(save_path_projected, f"{var_sisepuede}.csv")

all_projected_df.to_csv(file_save_path_projected, index = False)