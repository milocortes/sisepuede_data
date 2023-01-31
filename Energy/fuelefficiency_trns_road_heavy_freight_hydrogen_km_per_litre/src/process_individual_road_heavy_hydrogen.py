import os 
import sys
import pandas as pd

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()


save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 


# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]

# Build and save to csv historical data

'''
    - Fuel consumption rates are around 8 kg-H2/100 km (Liu et al., 2021, p. 17987)
    - The fuel economy improvement rate is set at 1 % from 2020 to 2050 for fuel cell (Ou et al., 2013; Chen and
Melaina, 2019).

    1 Kilogram of Hydrogen is equal to 14.128 Liters

    In terms of liters:
    - Fuel consumption rates are around 113.024/100 km 
    - Convert LGE/100km  unit to sisepuede unit km/l [ km/l = ((LGE/100km)^-1)*(100)  ].
'''

#var_energy_to_process = "fuelefficiency_trns_road_heavy_freight_hydrogen_km_per_litre"
var_energy_to_process = sys.argv[1]

time = range(2000, 2020)

hydrogen_km_to_liters = ((8 * 14.128)**-1)*100
df_var_energy = pd.DataFrame({"Year" : time, var_energy_to_process : [hydrogen_km_to_liters]*len(time)})

historical_df_var_energy = iso3_m49_correspondence.merge(right = df_var_energy, how = "cross") 

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

file_save_path_historical = os.path.join(save_path_historical, f"{var_energy_to_process}.csv")
historical_df_var_energy.to_csv(file_save_path_historical, index = False)

# Build and save to csv projected data
last_year = df_var_energy["Year"].to_list()[-1]
time_period = range(last_year +1, 2051)

# Build projected value
# The fuel economy improvement rate is set at 1 % from 2020 to 2050 for fuel cell
last_value = df_var_energy[var_energy_to_process].to_list()[-1]
projected_val_list = [0]*len(time_period)
projected_val_list[0] = last_value

for i in range(1, len(projected_val_list)):
    projected_val_list[i] = projected_val_list[i-1]*1.01

projected_df_var_energy = pd.DataFrame({"Year" : time_period, var_energy_to_process : projected_val_list})

all_projected_df_var_energy = iso3_m49_correspondence.merge( right = projected_df_var_energy, how = "cross")


save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

file_save_path_projected = os.path.join(save_path_projected, f"{var_energy_to_process}.csv")

all_projected_df_var_energy.to_csv(file_save_path_projected, index = False)