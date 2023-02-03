import os 
import sys
import pandas as pd
from correspondences import correspondencias_regional_to_freight, correspondencias_freight_to_regional

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ,"USA_transportation_energy_data" )) 

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 


# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]

# Build and save to csv historical data
#var_energy_to_process = "frac_trns_fuelmix_road_light_biofuels"
var_energy_to_process = correspondencias_regional_to_freight[sys.argv[1]]

file_var_energy_path = os.path.join(sources_path, f"{var_energy_to_process}.csv")

df_var_energy = pd.read_csv(file_var_energy_path)

historical_df_var_energy = iso3_m49_correspondence.merge(right = df_var_energy, how = "cross") 
historical_df_var_energy.rename(columns = {var_energy_to_process : correspondencias_freight_to_regional[var_energy_to_process]}, inplace = True)
save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

file_save_path_historical = os.path.join(save_path_historical, f"{correspondencias_freight_to_regional[var_energy_to_process]}.csv")
historical_df_var_energy.to_csv(file_save_path_historical, index = False)

# Build and save to csv projected data
last_value = df_var_energy[var_energy_to_process].to_list()[-1]
last_year = df_var_energy["Year"].to_list()[-1]

time_period = range(last_year +1, 2051)

projected_df_var_energy = pd.DataFrame({"Year" : time_period, correspondencias_freight_to_regional[var_energy_to_process] : [last_value]*len(time_period)})

all_projected_df_var_energy = iso3_m49_correspondence.merge( right = projected_df_var_energy, how = "cross")


save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

file_save_path_projected = os.path.join(save_path_projected, f"{correspondencias_freight_to_regional[var_energy_to_process]}.csv")

all_projected_df_var_energy.to_csv(file_save_path_projected, index = False)