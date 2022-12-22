import pandas as pd
import numpy as np
import os 

# Get oil GW
variable_to_process = "oil"
sisepuede_name = f"nemomod_entc_residual_capacity_pp_{variable_to_process}_gw"

print(f"Processing {sisepuede_name} variable")

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))

relative_path = os.path.normpath(dir_path + "/../../../")
relative_path_power_plants_file = os.path.join(relative_path, "global_power_plant_database" ,"global_power_plant_database.csv")

# Read source 
power_plants = pd.read_csv(relative_path_power_plants_file)

# Get countries ISO 3 codes
relative_path_iso3_file = os.path.join(relative_path, "iso3_all_countries.csv")
iso3_countries = pd.read_csv(relative_path_iso3_file)

# Build correspondence with iso3_countries (Only latin America)
latam_countries = iso3_countries["Category Name"][:26]
resto_countries = iso3_countries["Category Name"][26:]

sisepuede_countries_match_latam = list(set(power_plants[power_plants["country_long"].isin(latam_countries)]["country_long"]))
sisepuede_countries_resto_latam = list(set(latam_countries).symmetric_difference(sisepuede_countries_match_latam))

sisepuede_countries_match_all_countries = list(set(power_plants[power_plants["country_long"].isin(resto_countries)]["country_long"]))


# Energy types dictionary  

energy_type = { 'biogas' : 'Other',
                'biomass' : 'Biomass',
                'coal' : 'Coal',
                'gas' : 'Gas',
                'geothermal' : 'Geothermal',
                'incineration' : 'Other',
                'hydropower' : 'Hydro',
                'ocean' : 'Other',
                'nuclear' : 'Nuclear',
                'oil' : 'Oil',
                'solar' : 'Solar',
                'wind' : 'Wind'}


# Subset by energy type
power_plants = power_plants[power_plants["primary_fuel"] == energy_type[variable_to_process]]

# Subset all registers with Commissioning Year
power_plants = power_plants[~power_plants["commissioning_year"].isna()]
# Subsets all operational power plants
#power_plants = power_plants.query("Unit_status=='Operational'")

# If Decommissioning Year is empty, add 2200 value
#power_plants["Decommissioning Year"] = power_plants["Decommissioning Year"].replace(np.nan, 2200)

# Convert Decommissioning Year and Commissioning Year to int
#power_plants["Decommissioning Year"] = power_plants["Decommissioning Year"].astype("int")
power_plants["commissioning_year"] = power_plants["commissioning_year"].astype("int")

# Rename 'United States of America' --> United States
power_plants.loc[power_plants["country_long"]=='United States of America',"country_long"] = "United States"
power_plants.loc[power_plants["country_long"]=='North Korea',"country_long"] = 'Korea, Dem. Rep.'
power_plants.loc[power_plants["country_long"]=='South Korea',"country_long"] = 'Korea, Rep.'
power_plants.loc[power_plants["country_long"]=='Iran',"country_long"] = 'Iran, Islamic Rep.'
power_plants.loc[power_plants["country_long"]=='Ethiopia',"country_long"] = 'Ethiopia (includes Eritrea)'
power_plants.loc[power_plants["country_long"]=='Democratic Republic of the Congo',"country_long"] = 'Congo, Rep.'
power_plants.loc[power_plants["country_long"]=='Russia',"country_long"] = 'Russian Federation'
power_plants.loc[power_plants["country_long"]=='Egypt',"country_long"] = 'Egypt, Arab Rep.'
power_plants.loc[power_plants["country_long"]=='Laos',"country_long"] = 'Lao PDR'

power_plants = power_plants.query("country_long != 'Yemen'")
power_plants = power_plants.query("country_long != 'Antarctica'")

year = 1970
acumula_query = []


while year < 2022:
    
    print(year)
    # Subset time period range
    consulta = (power_plants["commissioning_year"] <= year) 
    query_power_plants = power_plants[consulta].reset_index(drop = True)

    # Group by countries
    query_power_plants = query_power_plants[["country_long", "capacity_mw"]]
    series_power_plants = query_power_plants.groupby("country_long").sum()
    series_power_plants_countries = series_power_plants.index
    resto_power_plants_countries = set(iso3_countries["Category Name"]).symmetric_difference(series_power_plants_countries)

    for c in series_power_plants_countries:
        query_list = iso3_countries.set_index("Category Name").loc[c,["REGION","ISO3","Code"]].tolist() 
        query_list.append(year)
        query_list.append(series_power_plants.loc[c].values[0])
        acumula_query.append(query_list)

    for c in resto_power_plants_countries:
        query_list = iso3_countries.set_index("Category Name").loc[c,["REGION","ISO3","Code"]].tolist() 
        query_list.append(year)
        query_list.append(0)
        acumula_query.append(query_list)
    
    
    year += 1

## Convert to dataframe
df_energy_pp = pd.DataFrame(acumula_query, columns = ["Nation", "ISO3", "Code", "Year", sisepuede_name])
df_energy_pp = df_energy_pp.sort_values(["Nation","Year"])

## Convert MW (Megavatio) to GW (Gigavatio)
factor = 0.001
df_energy_pp[sisepuede_name] = df_energy_pp[sisepuede_name]*factor 

## Save historical data

relative_path_to_save_historical = os.path.normpath(dir_path + "/../input_to_sisepuede/historical")
relative_path_to_save_historical_file = os.path.join(relative_path_to_save_historical, f"{sisepuede_name}.csv")


df_energy_pp.rename(columns = {"ISO3":"iso_code3"}, inplace = True)
df_energy_pp[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_historical_file, index = False)

## Get the last one historical year
last_one_year = max(df_energy_pp["Year"])
loy_df_energy_pp = df_energy_pp.query(f"Year=={last_one_year}").reset_index(drop=True)

## Project with the last value to 2050

acumula_df = []

for i in range(last_one_year, 2050):
    last_one_year += 1
    new_loy_df = loy_df_energy_pp.copy()
    new_loy_df["Year"] = last_one_year
    acumula_df.append(new_loy_df)

df_project = pd.concat(acumula_df, ignore_index = True)
df_project.sort_values(["Nation","Year"], inplace = True)

## Save projected data
relative_path_to_save_projected = os.path.normpath(dir_path + "/../input_to_sisepuede/projected")
relative_path_to_save_projected_file = os.path.join(relative_path_to_save_projected, f"{sisepuede_name}.csv")

df_project[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_projected_file, index = False)