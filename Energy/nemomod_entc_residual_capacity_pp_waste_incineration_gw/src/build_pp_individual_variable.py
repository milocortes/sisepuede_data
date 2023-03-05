import os 
import sys
import pandas as pd

# Set directories
sisepuede_name = sys.argv[1]

print(f"Processing {sisepuede_name} variable")

dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

relative_path = os.path.normpath(dir_path + "/../raw_data")
relative_path_power_plants_file = os.path.join(relative_path, "inputs_by_country_modvar_entc_nemomod_residual_capacity.csv.tar.gz")

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 
save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

# Load power plants data
pp_plants = pd.read_csv(relative_path_power_plants_file)
pp_plants.rename(columns = {"inputs_by_country_modvar_entc_nemomod_residual_capacity.csv" : "Year", "country" : "Nation"}, inplace = True)
pp_plants = pp_plants[~pp_plants["Year"].isnull()]
pp_plants["Year"] = pp_plants["Year"].astype(int)

# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]

# Merge iso code 3
pp_plants = pp_plants.merge(right = iso3_m49_correspondence, how = "inner", on = "Nation")

# Get minimal data

if sisepuede_name in ['nemomod_entc_residual_capacity_pp_biogas_gw', 'nemomod_entc_residual_capacity_pp_ocean_gw']:
    pp_plants[sisepuede_name] = pp_plants["pp_other"]*0.5

pp_plants = pp_plants[["Year", "Nation", "iso_code3", sisepuede_name]]

# Variables de sisepuede que nos faltan
sisepuede_paises = pd.read_html("https://sisepuede.readthedocs.io/en/latest/general_data.html")[-1]
sisepuede_faltantes = list(set(sisepuede_paises["Category Name"]).symmetric_difference(set(pp_plants.Nation).intersection(sisepuede_paises["Category Name"])))

# Obtenemos el promedio de la región
sisepuede_si_tengo = sisepuede_paises[~sisepuede_paises["Category Name"].isin(sisepuede_faltantes)]["Category Name"].to_list()

region_mean = pp_plants[pp_plants.Nation.isin(sisepuede_si_tengo)][["Year", "iso_code3",sisepuede_name]].groupby("Year").mean()[sisepuede_name].values
years = pp_plants[pp_plants.Nation.isin(sisepuede_si_tengo)][["Year", "iso_code3",sisepuede_name]].groupby("Year").mean().index.values

iso3_m49_correspondence["Nation"] = iso3_m49_correspondence["Nation"].replace({"Venezuela (Bolivarian Republic of)" : "Venezuela", 'Bolivia (Plurinational State of)' : "Bolivia"})

for faltantes_country in sisepuede_faltantes:
    pais_nombre_faltante,pais_iso_code3_faltante = iso3_m49_correspondence.loc[iso3_m49_correspondence["Nation"]==faltantes_country].to_numpy()[0]  

    df_partial = pd.DataFrame({"Year" : years, "Nation" : [pais_nombre_faltante]*len(years), "iso_code3" : [pais_iso_code3_faltante]*len(years), sisepuede_name : region_mean})
    pp_plants = pd.concat([pp_plants, df_partial], ignore_index = True)
    
# Historical data <= 2020
# Projected data > 2020

threshold_year = 2020

pp_plants_historical = pp_plants.query(f"Year <= {threshold_year}").reset_index(drop = True)
pp_plants_projected = pp_plants.query(f"Year > {threshold_year}").reset_index(drop = True)

## Save historical data
relative_path_to_save_historical_file = os.path.join(save_path_historical, f"{sisepuede_name}.csv")
pp_plants_historical.to_csv(relative_path_to_save_historical_file, index = False)

## Save projected data
relative_path_to_save_projected_file = os.path.join(save_path_projected, f"{sisepuede_name}.csv")
pp_plants_projected.to_csv(relative_path_to_save_projected_file, index = False)
