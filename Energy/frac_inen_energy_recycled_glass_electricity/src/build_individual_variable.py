import pandas as pd
import os 
import sys

# Get argument

sisepuede_var = sys.argv[1]

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ))

## Load historical data
historical_path = os.path.join(sources_path,"frac_inen_sisepuede_industry_fuels_data.csv.bz2")
historical_data = pd.read_csv(historical_path)

## Load projected data
projected_path = os.path.join(sources_path,"frac_inen_sisepuede_industry_fuels_data_projected.csv.bz2")
projected_data = pd.read_csv(projected_path)

## Save historical data
save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 
save_path_historical_file = os.path.join(save_path_historical, f"{sisepuede_var}.csv") 

country_eeih_fuel_industries_cw_long_historical = historical_data[["iso_code3", "Nation", "Year", sisepuede_var]].query("Year<=2020")

country_eeih_fuel_industries_cw_long_historical.to_csv(save_path_historical_file, index = False)

## Save historical data
save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))
save_path_projected_file = os.path.join(save_path, "projected", f"{sisepuede_var}.csv") 

country_eeih_fuel_industries_cw_long_projected = projected_data[["iso_code3", "Nation", "Year", sisepuede_var]].query("Year>2020")
country_eeih_fuel_industries_cw_long_projected.to_csv(save_path_projected_file, index = False)
