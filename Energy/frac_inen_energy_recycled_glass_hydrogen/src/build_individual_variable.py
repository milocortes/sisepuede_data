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

## Save historical data
df_sisepuede_var_name = historical_data.query(f"frac_inen_energy_ == '{sisepuede_var}'")[["Country", "iso_code3", "variable", "frac_inen"]]
df_sisepuede_var_name.rename(columns = {"Country" :  "Nation", "variable" : "Year", "frac_inen" : sisepuede_var}, inplace = True)

save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))
save_path_historical_file = os.path.join(save_path, "historical", f"{sisepuede_var}.csv") 

df_sisepuede_var_name.to_csv(save_path_historical_file, index = False)

## Load projected data
projected_path = os.path.join(sources_path,"frac_inen_sisepuede_industry_fuels_data_projected.csv.bz2")
projected_data = pd.read_csv(projected_path)

## Save historical data
df_sisepuede_var_name = projected_data.query(f"frac_inen_energy_ == '{sisepuede_var}'")[["Country", "iso_code3", "variable", "frac_inen"]]
df_sisepuede_var_name.rename(columns = {"Country" :  "Nation", "variable" : "Year", "frac_inen" : sisepuede_var}, inplace = True)

save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))
save_path_projected_file = os.path.join(save_path, "projected", f"{sisepuede_var}.csv") 

df_sisepuede_var_name.to_csv(save_path_projected_file, index = False)


