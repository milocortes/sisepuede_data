from assumption import historical_assumption, projected_assumption
import os 
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()


save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 


# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]

var_energy_to_process = sys.argv[1]

time = range(2000, 2015)
# Compared to internal combustion engines, fuel cell technology can achieve a higher efficiency of 65% when compared to roughly 40% 
df_var_energy = pd.DataFrame({"Year" : time, var_energy_to_process : [historical_assumption["fuelefficiency_trns_water_borne_diesel_km_per_litre"]* 1.65]*len(time)})

historical_df_var_energy = iso3_m49_correspondence.merge(right = df_var_energy, how = "cross") 

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

file_save_path_historical = os.path.join(save_path_historical, f"{var_energy_to_process}.csv")
historical_df_var_energy.to_csv(file_save_path_historical, index = False)

# Build and save to csv projected data
last_year = df_var_energy["Year"].to_list()[-1]
last_value = df_var_energy[var_energy_to_process].to_list()[-1]
time_period = range(last_year +1, 2051)



projected_df_var_energy = pd.DataFrame({"Year" : time_period, var_energy_to_process : [last_value] * len(time_period)})

all_projected_df_var_energy = iso3_m49_correspondence.merge( right = projected_df_var_energy, how = "cross")


save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

file_save_path_projected = os.path.join(save_path_projected, f"{var_energy_to_process}.csv")

all_projected_df_var_energy.to_csv(file_save_path_projected, index = False)
