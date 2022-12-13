import pandas as pd
import numpy as np 

power_plants = pd.read_csv("../../../Plants_enerdata.csv")

# Get country list
country_list = list(set(power_plants["Country"]))

# Build correspondence with sisepuede_countries_iso3.csv
sisepuede_countries = pd.read_csv("../../../sisepuede_countries_iso3.csv")
sisepuede_countries_match = list(set(power_plants[power_plants["Country"].isin(sisepuede_countries["Category Name"])]["Country"]))
sisepuede_countries_resto = list(set(sisepuede_countries["Category Name"]).symmetric_difference(sisepuede_countries_match))

# Energy types dictionary  

energy_type = { 'biogas' : 'Biogas',
                'biomass' : 'Biomass',
                'coal' : 'Coal',
                'gas' : 'Gas',
                'geothermal' : 'Geothermal',
                'incineration' : 'Heat',
                'hydropower' : 'Hydro',
                'ocean' : 'Marine energy',
                'nuclear' : 'Nuclear',
                'oil' : 'Oil',
                'solar' : 'Solar',
                'wind' : 'Wind'}


# Get biogas GW
variable_to_process = "ocean"
sisepuede_name = f"nemomod_entc_residual_capacity_pp_{variable_to_process}_gw"

# Subset by energy type
power_plants = power_plants[power_plants["Energy 1"] == energy_type[variable_to_process]]

# Subset all registers with Commissioning Year
power_plants = power_plants[~power_plants["Commissioning Year"].isna()]
# Subsets all operational power plants
power_plants = power_plants.query("Unit_status=='Operational'")

# If Decommissioning Year is empty, add 2200 value
power_plants["Decommissioning Year"] = power_plants["Decommissioning Year"].replace(np.nan, 2200)

# Convert Decommissioning Year and Commissioning Year to int
power_plants["Decommissioning Year"] = power_plants["Decommissioning Year"].astype("int")
power_plants["Commissioning Year"] = power_plants["Commissioning Year"].astype("int")


year = 1970
acumula_query = []

while year < 2022:
    
    print(year)
    # Subset time period range
    consulta = (power_plants["Commissioning Year"] <= year) & (power_plants["Decommissioning Year"] != year) 
    query_power_plants = power_plants[consulta].reset_index(drop = True)

    # Group by countries
    query_power_plants = query_power_plants[["Country", "Net capacity (MW)"]]
    series_power_plants = query_power_plants.groupby("Country").sum()
    series_power_plants_countries = series_power_plants.index
    resto_power_plants_countries = set(sisepuede_countries["Category Name"]).symmetric_difference(series_power_plants_countries)

    for c in series_power_plants_countries:
        query_list = sisepuede_countries.set_index("Category Name").loc[c,["REGION","ISO3","Code"]].tolist() 
        query_list.append(year)
        query_list.append(series_power_plants.loc[c].values[0])
        acumula_query.append(query_list)

    for c in resto_power_plants_countries:
        query_list = sisepuede_countries.set_index("Category Name").loc[c,["REGION","ISO3","Code"]].tolist() 
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
df_energy_pp.rename(columns = {"ISO3":"iso_code3"}, inplace = True)
df_energy_pp.to_csv(f"../input_to_sisepuede/historical/{sisepuede_name}.csv", index = False)

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
df_project.to_csv(f"../input_to_sisepuede/projected/{sisepuede_name}.csv", index = False)