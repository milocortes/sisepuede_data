import os 
import sys
import pandas as pd

# Set directories
sisepuede_name = sys.argv[1]

print(f"Processing {sisepuede_name} variable")

dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

relative_path = os.path.normpath(dir_path + "/../raw_data")
relative_path_file = os.path.join(relative_path, "frac_trns_fuelmix_powered_bikes.csv")

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 
save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

# Load data
frac_bikes = pd.read_csv(relative_path_file)

# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]
iso3_m49_correspondence["Nation"] = iso3_m49_correspondence["Nation"].replace({"Türkiye" : "Turkey"})

# Build and save to csv historical data
# Merge iso code 3
frac_bikes = frac_bikes[["year", sisepuede_name]]
frac_bikes.rename(columns = {"year":"Year"}, inplace = True)

historical_df_var_energy = iso3_m49_correspondence.merge(right = frac_bikes, how = "cross") 


file_save_path_historical = os.path.join(save_path_historical, f"{sisepuede_name}.csv")
historical_df_var_energy.to_csv(file_save_path_historical, index = False)


# Build and save to csv projected data
last_value = frac_bikes[sisepuede_name].to_list()[-1]
last_year = frac_bikes["Year"].to_list()[-1]

time_period = range(last_year +1, 2051)

projected_df_frac_bikes = pd.DataFrame({"Year" : time_period, sisepuede_name : [last_value]*len(time_period)})

all_projected_df_frac_bikes = iso3_m49_correspondence.merge( right = projected_df_frac_bikes, how = "cross")


save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

file_save_path_projected = os.path.join(save_path_projected, f"{sisepuede_name}.csv")

all_projected_df_frac_bikes.to_csv(file_save_path_projected, index = False)
