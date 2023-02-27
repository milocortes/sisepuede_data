import pandas as pd
import matplotlib.pyplot as plt
import os 

from sectors_assumptions import industries_correspondence, fuels_correspondence, industries_correspondence_recycled

# Set directories
#dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ))
eei_industry_path = os.path.join(sources_path,"eei industry.csv")

save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))

## Load ISO3 codes
iso3_code_path = os.path.join(sources_path,"iso3_countries.csv")

iso3_code = pd.read_csv(iso3_code_path)
iso3_code.dropna(inplace = True)

iso3_code = iso3_code[["Continent", "Name", "ISO 3"]]

## Load eei industry
df_eei_industry = pd.read_csv(eei_industry_path)

# Rename countries
dict_rename_countries = {'Republic of Moldova' : 'Moldova, Republic of', 
                         'Slovak Republic' : 'Slovakia',
                         'Korea' : 'Korea, Republic of'}

for original_name, iso_name in dict_rename_countries.items():
    df_eei_industry.loc[df_eei_industry["COUNTRY"]==original_name, "COUNTRY"] = iso_name 

# Merge continent column
iso3_code.rename(columns = {"Name": "Country"}, inplace = True)
df_eei_industry.rename(columns = {"COUNTRY" : "Country"}, inplace = True)

df_eei_industry = df_eei_industry.merge(right = iso3_code[["Country", "Continent"]], how = "inner", on = "Country")

# Remove non numeric values
for year in range(2000, 2017):
    df_eei_industry = df_eei_industry[df_eei_industry[f"{year}"] != 'x'] 
    df_eei_industry = df_eei_industry[df_eei_industry[f"{year}"] != 'xxx'] 
    df_eei_industry = df_eei_industry[df_eei_industry[f"{year}"] != '..']
    df_eei_industry[f"{year}"] = df_eei_industry[f"{year}"].astype(float)

# Subset only energy variables
# 'Total final energy (PJ)' = 'Coal and coal products (PJ)' + 'Combustible renewables and waste (PJ)' + 'Electricity (PJ)' + 'Gas (PJ)' + 'Heat (PJ)' + 'Oil and oil products (PJ)' + 'Other sources (PJ)'
energy_vars = ['Coal and coal products (PJ)', 'Combustible renewables and waste (PJ)', 'Electricity (PJ)', 'Gas (PJ)', 'Heat (PJ)', 'Oil and oil products (PJ)', 'Other sources (PJ)']

df_eei_industry = df_eei_industry[df_eei_industry["PRODUCT/FLOW"].isin(energy_vars)] 


# Refactor to sisepuede variables
acumula_sispuede_dfs = []

for sisepuede_var, info_correspondence in industries_correspondence.items():
    factor, eia_var = info_correspondence

    print(f"{sisepuede_var} -----> {eia_var}")
    left_df = df_eei_industry.query(f"ENDUSE == '{eia_var}'")[["Country", "PRODUCT/FLOW", "ENDUSE", "Continent"]]
    # Multiply by factor
    right_df = df_eei_industry.query(f"ENDUSE == '{eia_var}'")[[str(y) for y in range(2000, 2017)]]*factor
    # Set ENDUSE column to the sisepuede correspondence
    left_df["ENDUSE"] = sisepuede_var

    # Concat dataframes
    df_sisepuede_var = pd.concat([left_df, right_df], axis = 1)
    print(df_sisepuede_var.shape)
    acumula_sispuede_dfs.append(df_sisepuede_var)

    # Append if the sisepuede variable has a correspondence with a recycled variable 

    if sisepuede_var in industries_correspondence_recycled:
        df_sisepuede_var_recycled = df_sisepuede_var.copy()
        df_sisepuede_var_recycled["ENDUSE"] = industries_correspondence_recycled[sisepuede_var]
        print(f"{industries_correspondence_recycled[sisepuede_var]} -----> {sisepuede_var}")
        print(df_sisepuede_var_recycled.shape)
        acumula_sispuede_dfs.append(df_sisepuede_var_recycled)

df_sisepuede_industry = pd.concat(acumula_sispuede_dfs, ignore_index = True)


# Refactor to sisepuede fuels
acumula_sispuede_dfs_fuels = []

for sisepuede_fuel, info_correspondence in fuels_correspondence.items():

    if info_correspondence:
        factor, eia_fuel = info_correspondence

        print(f"{sisepuede_fuel} -----> {eia_fuel}")

        left_df = df_sisepuede_industry[df_sisepuede_industry["PRODUCT/FLOW"]==eia_fuel][["Country", "PRODUCT/FLOW", "ENDUSE", "Continent"]]
        # Multiply by factor
        right_df = df_sisepuede_industry[df_sisepuede_industry["PRODUCT/FLOW"]==eia_fuel][[str(y) for y in range(2000, 2017)]]*factor
        # Set ENDUSE column to the sisepuede correspondence
        left_df["PRODUCT/FLOW"] = sisepuede_fuel

        # Concat dataframes
        df_sisepuede_fuel = pd.concat([left_df, right_df], axis = 1)
        print(df_sisepuede_fuel.shape)

        acumula_sispuede_dfs_fuels.append(df_sisepuede_fuel)

df_sisepuede_industry_fuels = pd.concat(acumula_sispuede_dfs_fuels, ignore_index = True)


# Change format to long format
l_df_sisepuede_industry_fuels = df_sisepuede_industry_fuels.melt(id_vars = ["Continent", "Country", "PRODUCT/FLOW", "ENDUSE"])

l_df_sisepuede_industry_fuels["variable"] = l_df_sisepuede_industry_fuels["variable"].astype(int) 
l_df_sisepuede_industry_fuels["value"] = l_df_sisepuede_industry_fuels["value"].astype(float) 

# Build frac_inen variable by country
countries = set(l_df_sisepuede_industry_fuels["Country"] )
years = set(l_df_sisepuede_industry_fuels["variable"])
enduses = set(l_df_sisepuede_industry_fuels["ENDUSE"])

acumula_country_df = []

for country in countries:
    print(f"{country}")
    for enduse in enduses:
        print(f"{enduse}")
        for year in years:
            partial_df = l_df_sisepuede_industry_fuels.query(f"Country == '{country}' and ENDUSE == '{enduse}' and variable == {year}")
            partial_df["frac_inen"] = partial_df["value"].transform(lambda x: x/x.sum())

            acumula_country_df.append(partial_df)

frac_inen_country_sisepuede_industry_fuels = pd.concat(acumula_country_df, ignore_index = True)
frac_inen_country_sisepuede_industry_fuels = frac_inen_country_sisepuede_industry_fuels.sort_values(by = ["Country","ENDUSE","PRODUCT/FLOW","variable"])      
frac_inen_country_sisepuede_industry_fuels = frac_inen_country_sisepuede_industry_fuels.fillna(0)
## Test sum
frac_inen_country_sisepuede_industry_fuels.query("Country == 'Australia' and ENDUSE == 'paper' and variable == 2000")

ax = frac_inen_country_sisepuede_industry_fuels.query("Country == 'Australia' and ENDUSE == 'paper' and variable == 2000").plot.bar(x='PRODUCT/FLOW', y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Country == 'Australia' and ENDUSE == 'paper' and variable == 2000")
plt.show()

# Group by continent and ENDUSE

continent_df_sisepuede_industry_fuels = l_df_sisepuede_industry_fuels[['Continent', 'PRODUCT/FLOW', 'ENDUSE', 'variable', 'value']].groupby(['Continent', 'PRODUCT/FLOW', 'ENDUSE', 'variable']).sum().reset_index()

# Build frac_inen variable by continent
continents = set(continent_df_sisepuede_industry_fuels["Continent"] )
years = set(continent_df_sisepuede_industry_fuels["variable"])
enduses = set(continent_df_sisepuede_industry_fuels["ENDUSE"])

acumula_continent_df = []

for continent in continents:
    print(f"{continent}")
    for enduse in enduses:
        print(f"{enduse}")
        for year in years:
            partial_df = continent_df_sisepuede_industry_fuels.query(f"Continent == '{continent}' and ENDUSE == '{enduse}' and variable == {year}")
            partial_df["frac_inen"] = partial_df["value"].transform(lambda x: x/x.sum())

            acumula_continent_df.append(partial_df)

frac_inen_continent_df_sisepuede_industry_fuels = pd.concat(acumula_continent_df, ignore_index = True)
frac_inen_continent_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels.sort_values(by = ["Continent","ENDUSE","PRODUCT/FLOW","variable"])      
frac_inen_continent_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels.fillna(0)

## Test sum
frac_inen_continent_df_sisepuede_industry_fuels.query("Continent == 'EU' and ENDUSE == 'paper' and variable == 2000")

ax = frac_inen_continent_df_sisepuede_industry_fuels.query("Continent == 'EU' and ENDUSE == 'paper' and variable == 2000").plot.bar(x='PRODUCT/FLOW', y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Continent == 'EU' and ENDUSE == 'paper' and variable == 2000")
plt.show()

### Build frac_inen variable world

frac_inen_world_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels[["PRODUCT/FLOW", "ENDUSE", "variable", "value"]].groupby(["PRODUCT/FLOW", "ENDUSE", "variable"]).sum().reset_index() 

years = set(frac_inen_world_df_sisepuede_industry_fuels["variable"])
enduses = set(frac_inen_world_df_sisepuede_industry_fuels["ENDUSE"])

acumula_world_df = []


for enduse in enduses:
    print(f"{enduse}")
    for year in years:
        partial_df = frac_inen_world_df_sisepuede_industry_fuels.query(f"ENDUSE == '{enduse}' and variable == {year}")
        partial_df["frac_inen"] = partial_df["value"].transform(lambda x: round(x/x.sum(),4))

        acumula_world_df.append(partial_df)

frac_inen_world_df_sisepuede_industry_fuels = pd.concat(acumula_world_df, ignore_index = True)
frac_inen_world_df_sisepuede_industry_fuels = frac_inen_world_df_sisepuede_industry_fuels.sort_values(by = ["ENDUSE","PRODUCT/FLOW","variable"])      

frac_inen_world_df_sisepuede_industry_fuels = frac_inen_world_df_sisepuede_industry_fuels.fillna(0)

## Test sum
frac_inen_world_df_sisepuede_industry_fuels.query("ENDUSE == 'paper' and variable == 2000")

ax = frac_inen_world_df_sisepuede_industry_fuels.query("ENDUSE == 'paper' and variable == 2000").plot.bar(x='PRODUCT/FLOW', y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("ENDUSE == 'paper' and variable == 2000")
plt.show()

### Build data for all countries

iso3_code.set_index("Country", inplace = True)

acumula_all_countries = []
columnas_pd = ["Country", "iso_code3","PRODUCT/FLOW", "ENDUSE", "variable", "value", "frac_inen"]

for country in iso3_code.index:
    continent, ISO3 = iso3_code.loc[country]

    ## is in country data?
    if country in frac_inen_country_sisepuede_industry_fuels["Country"].unique():
        df_country = frac_inen_country_sisepuede_industry_fuels.query(f"Country == '{country}'")
        df_country["iso_code3"] = ISO3
        df_country = df_country[columnas_pd]
        acumula_all_countries.append(df_country)
    ## is in continent data?
    elif continent in frac_inen_continent_df_sisepuede_industry_fuels["Continent"].unique():
        df_country = frac_inen_continent_df_sisepuede_industry_fuels.query(f"Continent == '{continent}'")
        df_country["Country"] = country
        df_country["iso_code3"] = ISO3
        df_country = df_country[columnas_pd]
        acumula_all_countries.append(df_country)

    ## Set world value
    else:
        df_country = frac_inen_world_df_sisepuede_industry_fuels.copy()
        df_country["Country"] = country
        df_country["iso_code3"] = ISO3
        df_country = df_country[columnas_pd]       
        acumula_all_countries.append(df_country)

frac_inen_all_countries = pd.concat(acumula_all_countries, ignore_index = True)

## Test sum
frac_inen_all_countries = frac_inen_all_countries.sort_values(["Country", "iso_code3","variable", "ENDUSE"])
frac_inen_all_countries.query("Country == 'Argentina' and ENDUSE == 'paper' and variable == 2000")

ax = frac_inen_all_countries.query("Country == 'Argentina' and ENDUSE == 'paper' and variable == 2000").plot.bar(x='PRODUCT/FLOW', y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Country == 'Argentina' and ENDUSE == 'paper' and variable == 2000")
plt.show()


## Add frac_inen_energy_ sisepuede variable
frac_inen_all_countries["frac_inen_energy_"] = frac_inen_all_countries["ENDUSE"].apply(lambda x : f"frac_inen_energy_{x}_") + frac_inen_all_countries["PRODUCT/FLOW"]

## Save data
frac_inen_sisepuede_industry_fuels = os.path.join(sources_path,"frac_inen_sisepuede_industry_fuels_data.csv")
frac_inen_all_countries.to_csv(frac_inen_sisepuede_industry_fuels, index = False)


## Save historical data
sisepuede_var_name = frac_inen_all_countries["frac_inen_energy_"].unique()

save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))


for svn in sisepuede_var_name:
    print(svn)
    df_sisepuede_var_name = frac_inen_all_countries.query(f"frac_inen_energy_ == '{svn}'")[["Country", "iso_code3", "variable", "frac_inen"]]
    df_sisepuede_var_name.rename(columns = {"Country" :  "Nation", "variable" : "Year", "frac_inen" : svn}, inplace = True)

    save_path_historical_file = os.path.join(save_path, "historical", f"{svn}.csv") 

    df_sisepuede_var_name.to_csv(save_path_historical_file, index = False)

## Build projected data

latest_year = max(frac_inen_all_countries["variable"])
projected_year = 2050
acumula_year = latest_year

frac_inen_all_countries_projected = frac_inen_all_countries.query(f"variable == {latest_year}")

acumula_projected = []

for i in range(latest_year +1, projected_year +1):
    acumula_year += 1
    partial_df = frac_inen_all_countries_projected.copy()

    partial_df["variable"] = acumula_year

    acumula_projected.append(partial_df)

frac_inen_all_countries_projected = pd.concat(acumula_projected, ignore_index = True)

## Save data
frac_inen_sisepuede_industry_fuels = os.path.join(sources_path,"frac_inen_sisepuede_industry_fuels_data_projected.csv")
frac_inen_all_countries_projected.to_csv(frac_inen_sisepuede_industry_fuels, index = False)


## Save projected data

for svn in sisepuede_var_name:
    print(svn)
    df_sisepuede_var_name = frac_inen_all_countries.query(f"frac_inen_energy_ == '{svn}'")[["Country", "iso_code3", "variable", "frac_inen"]]
    df_sisepuede_var_name.rename(columns = {"Country" :  "Nation", "variable" : "Year", "frac_inen" : svn}, inplace = True)

    save_path_historical_file = os.path.join(save_path, "projected", f"{svn}.csv") 

    df_sisepuede_var_name.to_csv(save_path_historical_file, index = False)
