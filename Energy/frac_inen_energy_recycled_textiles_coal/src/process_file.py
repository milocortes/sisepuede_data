import pandas as pd
import matplotlib.pyplot as plt
import os 

from sectors_assumptions import industries_correspondence, fuels_correspondence, industries_correspondence_recycled

# Set directories
#dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ))
eei_industry_path = os.path.join(sources_path,"iea_industry_energy.csv")

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
                         'Korea' : 'Korea, Republic of',
                         'Hong Kong (China)' : 'Hong Kong',
                         'Republic of North Macedonia': 'Macedonia, the Former Yugoslav Republic of',
                         'Republic of Türkiye' : 'Turkey'}


df_eei_industry["Country"] = df_eei_industry["Country"].replace(dict_rename_countries)

# Merge continent column
iso3_code.rename(columns = {"Name": "Country"}, inplace = True)
df_eei_industry.rename(columns = {"Country" : "Country"}, inplace = True)


df_eei_industry = df_eei_industry.merge(right = iso3_code[["Country", "Continent"]], how = "inner", on = "Country")

# Remove non numeric values
for year in range(2000, 2020):
    '''
    df_eei_industry = df_eei_industry[df_eei_industry[f"{year}"] != 'x'] 
    df_eei_industry = df_eei_industry[df_eei_industry[f"{year}"] != 'xxx'] 
    df_eei_industry = df_eei_industry[df_eei_industry[f"{year}"] != '..']
    df_eei_industry[f"{year}"] = df_eei_industry[f"{year}"].astype(float)
    '''

    df_eei_industry[str(year)] = df_eei_industry[str(year)].apply(lambda x: str(x).replace('x', "0.0").replace('xxx', "0.0").replace('..', "0.0") ).astype(float)


# Subset only energy variables
# 'Total final energy (PJ)' = 'Coal and coal products (PJ)' + 'Combustible renewables and waste (PJ)' + 'Electricity (PJ)' + 'Gas (PJ)' + 'Heat (PJ)' + 'Oil and oil products (PJ)' + 'Other sources (PJ)'
energy_vars = ['Coal and coal products (PJ)', 'Combustible renewables and waste (PJ)', 'Electricity (PJ)', 'Gas (PJ)', 'Heat (PJ)', 'Oil and oil products (PJ)', 'Other sources (PJ)']

# Quitamos espacios en blanco innecesarios
df_eei_industry["Product"] = df_eei_industry["Product"].apply(lambda x : x.strip())
df_eei_industry = df_eei_industry[df_eei_industry["Product"].isin(energy_vars)] 


# Refactor to sisepuede variables
acumula_sispuede_dfs = []

for sisepuede_var, info_correspondence in industries_correspondence.items():
    factor, eia_var = info_correspondence

    print(f"{sisepuede_var} -----> {eia_var}")
    left_df = df_eei_industry.query(f"Subsector == '{eia_var}'")[["Country", "Product", "Subsector", "Continent"]]
    # Multiply by factor
    right_df = df_eei_industry.query(f"Subsector == '{eia_var}'")[[str(y) for y in range(2000, 2020)]]*factor
    # Set ENDUSE column to the sisepuede correspondence
    left_df["Subsector"] = sisepuede_var

    # Concat dataframes
    df_sisepuede_var = pd.concat([left_df, right_df], axis = 1)
    print(df_sisepuede_var.shape)
    acumula_sispuede_dfs.append(df_sisepuede_var)

    # Append if the sisepuede variable has a correspondence with a recycled variable 

    if sisepuede_var in industries_correspondence_recycled:
        df_sisepuede_var_recycled = df_sisepuede_var.copy()
        df_sisepuede_var_recycled["Subsector"] = industries_correspondence_recycled[sisepuede_var]
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

        left_df = df_sisepuede_industry[df_sisepuede_industry["Product"]==eia_fuel][["Country", "Product", "Subsector", "Continent"]]
        # Multiply by factor
        right_df = df_sisepuede_industry[df_sisepuede_industry["Product"]==eia_fuel][[str(y) for y in range(2000, 2020)]]*factor
        # Set ENDUSE column to the sisepuede correspondence
        left_df["Product"] = sisepuede_fuel

        # Concat dataframes
        df_sisepuede_fuel = pd.concat([left_df, right_df], axis = 1)
        print(df_sisepuede_fuel.shape)

        acumula_sispuede_dfs_fuels.append(df_sisepuede_fuel)

df_sisepuede_industry_fuels = pd.concat(acumula_sispuede_dfs_fuels, ignore_index = True)

# Change format to long format
l_df_sisepuede_industry_fuels = df_sisepuede_industry_fuels.melt(id_vars = ["Continent", "Country", "Product", "Subsector"])

l_df_sisepuede_industry_fuels["variable"] = l_df_sisepuede_industry_fuels["variable"].astype(int) 
l_df_sisepuede_industry_fuels["value"] = l_df_sisepuede_industry_fuels["value"].astype(float) 

# Build frac_inen variable by Country
countries = set(l_df_sisepuede_industry_fuels["Country"] )
years = set(l_df_sisepuede_industry_fuels["variable"])
enduses = set(l_df_sisepuede_industry_fuels["Subsector"])

acumula_country_df = []

for country in countries:
    print(f"{country}")
    for enduse in enduses:
        print(f"{enduse}")
        for year in years:
            partial_df = l_df_sisepuede_industry_fuels.query(f"Country == '{country}' and Subsector == '{enduse}' and variable == {year}")
            partial_df["frac_inen"] = partial_df["value"].transform(lambda x: x/x.sum())

            acumula_country_df.append(partial_df)

frac_inen_country_sisepuede_industry_fuels = pd.concat(acumula_country_df, ignore_index = True)
frac_inen_country_sisepuede_industry_fuels = frac_inen_country_sisepuede_industry_fuels.sort_values(by = ["Country","Subsector","Product","variable"])      
frac_inen_country_sisepuede_industry_fuels = frac_inen_country_sisepuede_industry_fuels.fillna(0)
## Test sum
frac_inen_country_sisepuede_industry_fuels.query("Country == 'Australia' and Subsector == 'paper' and variable == 2000")

ax = frac_inen_country_sisepuede_industry_fuels.query("Country == 'Australia' and Subsector == 'paper' and variable == 2000").plot.bar(x="Product", y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Country == 'Australia' and Subsector == 'paper' and variable == 2000")
plt.show()

## Test for all year and all countries

print("++++++++++++++++++++++++++++++++++++++++++++++")
print("        Test for all year and all countries    ")
print("++++++++++++++++++++++++++++++++++++++++++++++")

for fuel in frac_inen_country_sisepuede_industry_fuels["Subsector"].unique():
    print("************")
    print(f"  {fuel}    ")
    print("************")
    anios_fuel = []
    suma_frac_inen = []
    paises_con_dato_mayor_cero = []
    for year_inen in frac_inen_country_sisepuede_industry_fuels.variable.unique():
        consulta = f"Subsector == '{fuel}' and variable == {year_inen}"
        columnas_min = ["Country", "Product", "Subsector", "frac_inen"]
        anios_fuel.append(year_inen)
        suma_frac_inen.append(frac_inen_country_sisepuede_industry_fuels.query(consulta)[columnas_min].groupby(["Country", "Subsector"]).sum()["frac_inen"].sum())
        paises_con_dato_mayor_cero.append(len(frac_inen_country_sisepuede_industry_fuels.query(consulta)[columnas_min].query("frac_inen>0.0")["Country"].unique()))
    print(pd.DataFrame({"Year" : anios_fuel, "Suma" : suma_frac_inen, "#Paises_dato" : paises_con_dato_mayor_cero}))

## Test countries without Subsector values
print("++++++++++++++++++++++++++++++++++++++++++++++")
print("        Test countries without Subsector values    ")
print("++++++++++++++++++++++++++++++++++++++++++++++")

almacena_pais_subsector_zeros = []
completos_pais_subsector = [(country, subsector) for country in countries for subsector in enduses]

for country in countries:
    for subsector in enduses:
        min_columns = ["Country","Product","variable","frac_inen"]
        test_all_zero = frac_inen_country_sisepuede_industry_fuels.query(f"Country=='{country}' and Subsector =='{subsector}'")[min_columns]\
                                                  .pivot_table(index = ["Country","variable"], columns = "Product", values = "frac_inen").sum(1)

        if all(map(lambda x:x==0.0,test_all_zero)):
            '''
            print("********************************")
            print(f"     {subsector}")
            print("********************************")
            print(frac_inen_country_sisepuede_industry_fuels.query(f"Country=='{country}' and Subsector =='{subsector}'")[min_columns]\
                                                  .pivot_table(index = ["Country","variable"], columns = "Product", values = "frac_inen"))
            '''
            almacena_pais_subsector_zeros.append((country, subsector))

    
# Group by continent and ENDUSE

continent_df_sisepuede_industry_fuels = l_df_sisepuede_industry_fuels[['Continent', "Product", "Subsector", 'variable', 'value']].groupby(['Continent', "Product", "Subsector", 'variable']).sum().reset_index()

# Build frac_inen variable by continent
continents = set(continent_df_sisepuede_industry_fuels["Continent"] )
years = set(continent_df_sisepuede_industry_fuels["variable"])
enduses = set(continent_df_sisepuede_industry_fuels["Subsector"])

acumula_continent_df = []

for continent in continents:
    print(f"{continent}")
    for enduse in enduses:
        print(f"{enduse}")
        for year in years:
            partial_df = continent_df_sisepuede_industry_fuels.query(f"Continent == '{continent}' and Subsector == '{enduse}' and variable == {year}")
            partial_df["frac_inen"] = partial_df["value"].transform(lambda x: x/x.sum())

            acumula_continent_df.append(partial_df)

frac_inen_continent_df_sisepuede_industry_fuels = pd.concat(acumula_continent_df, ignore_index = True)
frac_inen_continent_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels.sort_values(by = ["Continent","Subsector","Product","variable"])      
frac_inen_continent_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels.fillna(0)

## Test sum
frac_inen_continent_df_sisepuede_industry_fuels.query("Continent == 'EU' and Subsector == 'paper' and variable == 2000")

ax = frac_inen_continent_df_sisepuede_industry_fuels.query("Continent == 'EU' and Subsector == 'paper' and variable == 2000").plot.bar(x="Product", y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Continent == 'EU' and Subsector == 'paper' and variable == 2000")
plt.show()


## Test for all year and all countries

print("++++++++++++++++++++++++++++++++++++++++++++++")
print("        Test for all year and all CONTINENTS    ")
print("++++++++++++++++++++++++++++++++++++++++++++++")

for fuel in frac_inen_continent_df_sisepuede_industry_fuels["Subsector"].unique():
    print("************")
    print(f"  {fuel}    ")
    print("************")
    anios_fuel = []
    suma_frac_inen = []

    for year_inen in frac_inen_continent_df_sisepuede_industry_fuels.variable.unique():
        consulta = f"Subsector == '{fuel}' and variable == {year_inen}"
        columnas_min = ["Continent", "Product", "Subsector", "frac_inen"]
        anios_fuel.append(year_inen)
        suma_frac_inen.append(frac_inen_continent_df_sisepuede_industry_fuels.query(consulta)[columnas_min].groupby(["Continent", "Subsector"]).sum()["frac_inen"].sum())
    
    print(pd.DataFrame({"Year" : anios_fuel, "Suma" : suma_frac_inen}))


## Test continents without Subsector values
print("++++++++++++++++++++++++++++++++++++++++++++++")
print("        Test continents without Subsector values    ")
print("++++++++++++++++++++++++++++++++++++++++++++++")

almacena_continente_subsector_zeros = []
completos_continente_subsector = [(continent, subsector) for continent in frac_inen_continent_df_sisepuede_industry_fuels.Continent.unique() for subsector in enduses]

for continent in frac_inen_continent_df_sisepuede_industry_fuels.Continent.unique():
    for subsector in enduses:
        min_columns = ["Continent","Product","variable","frac_inen"]
        test_all_zero = frac_inen_continent_df_sisepuede_industry_fuels.query(f"Continent=='{continent}' and Subsector =='{subsector}'")[min_columns]\
                                                  .pivot_table(index = ["Continent","variable"], columns = "Product", values = "frac_inen").sum(1)

        if all(map(lambda x:x==0.0,test_all_zero)):
            
            """
            print("********************************")
            print(f"     {subsector}")
            print("********************************")
            print(frac_inen_continent_df_sisepuede_industry_fuels.query(f"Continent=='{continent}' and Subsector =='{subsector}'")[min_columns]\
                                                  .pivot_table(index = ["Continent","variable"], columns = "Product", values = "frac_inen"))
            """
            almacena_continente_subsector_zeros.append((continent, subsector))

    

### Build frac_inen variable world

frac_inen_world_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels[["Product", "Subsector", "variable", "value"]].groupby(["Product", "Subsector", "variable"]).sum().reset_index() 

years = set(frac_inen_world_df_sisepuede_industry_fuels["variable"])
enduses = set(frac_inen_world_df_sisepuede_industry_fuels["Subsector"])

acumula_world_df = []


for enduse in enduses:
    print(f"{enduse}")
    for year in years:
        partial_df = frac_inen_world_df_sisepuede_industry_fuels.query(f"Subsector == '{enduse}' and variable == {year}")
        partial_df["frac_inen"] = partial_df["value"].transform(lambda x: round(x/x.sum(),4))

        acumula_world_df.append(partial_df)

frac_inen_world_df_sisepuede_industry_fuels = pd.concat(acumula_world_df, ignore_index = True)
frac_inen_world_df_sisepuede_industry_fuels = frac_inen_world_df_sisepuede_industry_fuels.sort_values(by = ["Subsector","Product","variable"])      

frac_inen_world_df_sisepuede_industry_fuels = frac_inen_world_df_sisepuede_industry_fuels.fillna(0)

## Test sum
frac_inen_world_df_sisepuede_industry_fuels.query("Subsector == 'recycled_rubber_and_leather' and variable == 2000")

ax = frac_inen_world_df_sisepuede_industry_fuels.query("Subsector == 'recycled_rubber_and_leather' and variable == 2000").plot.bar(x="Product", y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Subsector == 'paper' and variable == 2000")
plt.show()


print("++++++++++++++++++++++++++++++++++++++++++++++")
print("        Test for all year FOR WORLD    ")
print("++++++++++++++++++++++++++++++++++++++++++++++")

for fuel in frac_inen_world_df_sisepuede_industry_fuels["Subsector"].unique():
    print("************")
    print(f"  {fuel}    ")
    print("************")
    anios_fuel = []
    suma_frac_inen = []

    for year_inen in frac_inen_world_df_sisepuede_industry_fuels.variable.unique():
        consulta = f"Subsector == '{fuel}' and variable == {year_inen}"
        columnas_min = ["Product", "Subsector", "frac_inen"]
        anios_fuel.append(year_inen)
        suma_frac_inen.append(frac_inen_world_df_sisepuede_industry_fuels.query(consulta)[columnas_min].groupby( "Subsector").sum()["frac_inen"].sum())
    
    print(pd.DataFrame({"Year" : anios_fuel, "Suma" : suma_frac_inen}))

### Build data for all countries
print("""
Nuestros datos
 frac_inen_country_sisepuede_industry_fuels
 frac_inen_continent_df_sisepuede_industry_fuels
 frac_inen_world_df_sisepuede_industry_fuels
""")

## Primero eliminaremos los registros de los paises que no tienen información de un subsector para imputarlo después

tenemos_el_dato_country = list(set(completos_pais_subsector) - set(almacena_pais_subsector_zeros))
frac_inen_country_sisepuede_industry_fuels = frac_inen_country_sisepuede_industry_fuels\
                                                                                        .set_index(["Country","Subsector"])\
                                                                                        .loc[tenemos_el_dato_country]\
                                                                                        .reset_index()

frac_inen_country_sisepuede_industry_fuels = frac_inen_country_sisepuede_industry_fuels.merge(right = iso3_code[["Country", "ISO 3"]], how = "inner", on = "Country")
frac_inen_country_sisepuede_industry_fuels.rename(columns = {"ISO 3" : "iso_code3"}, inplace = True)

## Después eliminaremos los registros de los continentes que no tienen información de un subsector para imputarlo después
tenemos_el_dato_continente = list(set(completos_continente_subsector) - set(almacena_continente_subsector_zeros))
frac_inen_continent_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels\
                                                                                            .set_index(["Continent","Subsector"])\
                                                                                            .loc[tenemos_el_dato_continente]\
                                                                                            .reset_index()

iso3_code.set_index("Country", inplace = True)

acumula_all_countries = []
columnas_pd = ["Country", "iso_code3", "Product", "Subsector", "variable", "value", "frac_inen"]


for economic_sector in frac_inen_world_df_sisepuede_industry_fuels.Subsector.unique():

    sector_frac_inen_continent_df_sisepuede_industry_fuels = frac_inen_continent_df_sisepuede_industry_fuels.query(f"Subsector=='{economic_sector}'")
    sector_frac_inen_world_df_sisepuede_industry_fuels = frac_inen_world_df_sisepuede_industry_fuels.query(f"Subsector=='{economic_sector}'")

    for country in iso3_code.index:
        continent, ISO3 = iso3_code.loc[country]

        ## is in country data?
        if not (country, economic_sector) in tenemos_el_dato_country:

            ## is in continent data?
            if (continent, economic_sector) in tenemos_el_dato_continente:
                df_country = sector_frac_inen_continent_df_sisepuede_industry_fuels.query(f"Continent == '{continent}'").reset_index()
                df_country["Country"] = country
                df_country["iso_code3"] = ISO3
                df_country = df_country[columnas_pd]
                acumula_all_countries.append(df_country)

            ## Set world value
            else:
                df_country = sector_frac_inen_world_df_sisepuede_industry_fuels.reset_index()
                df_country["Country"] = country
                df_country["iso_code3"] = ISO3
                df_country = df_country[columnas_pd]       
                acumula_all_countries.append(df_country)

frac_inen_all_countries = pd.concat([frac_inen_country_sisepuede_industry_fuels[columnas_pd]] + acumula_all_countries, ignore_index = True)

### For the fuels hydrocarbon_gas_liquids, hydrogen, kerosene and solid_biomass, assume that the value is 0 for all subsectors
impute_fuels = list(set(fuels_correspondence) - set(frac_inen_all_countries.Product.unique()))

tuples_country_iso_code3 = list(set(frac_inen_all_countries[["Country","iso_code3"]].itertuples(index=False, name=None)))

all_subsectors_sisepuede = frac_inen_all_countries.Subsector.unique()
all_years_iea = frac_inen_all_countries.variable.unique()

df_fuels_subsectors_missing = pd.DataFrame(tuples_country_iso_code3, columns = ["Country","iso_code3"])\
                                                .merge(pd.DataFrame({"Product":impute_fuels}), how = "cross")\
                                                .merge(pd.DataFrame({"Subsector" : all_subsectors_sisepuede}), how = "cross")\
                                                .merge(pd.DataFrame({"variable" : all_years_iea}), how = "cross")\
                                                .merge(pd.DataFrame({"value" : [0.0], "frac_inen" : [0.0]}), how = "cross")

frac_inen_all_countries = pd.concat([frac_inen_all_countries, df_fuels_subsectors_missing], ignore_index = True)

## Test sum
frac_inen_all_countries = frac_inen_all_countries.sort_values(["Country", "iso_code3","variable", "Subsector"])
frac_inen_all_countries.query("Country == 'Argentina' and Subsector == 'paper' and variable == 2000")

ax = frac_inen_all_countries.query("Country == 'Argentina' and Subsector == 'paper' and variable == 2000").plot.bar(x="Product", y='frac_inen', rot=0)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
plt.title("Country == 'Argentina' and Subsector == 'paper' and variable == 2000")
plt.show()

## Add frac_inen_energy_ sisepuede variable
frac_inen_all_countries["frac_inen_energy_"] = frac_inen_all_countries["Subsector"].apply(lambda x : f"frac_inen_energy_{x}_") + frac_inen_all_countries["Product"]

## Test stacked bar plot

frac_inen_all_countries.query("Country=='Afghanistan' and Subsector =='other_product_manufacturing'")[["Product","variable","frac_inen"]]\
                       .pivot(index = 'variable', columns = 'Product', values='frac_inen').plot(kind='bar', stacked=True)
plt.title("Pais : Afghanistan.\nSector : other_product_manufacturing")
plt.show()

country = "Mexico"
for subsector in frac_inen_world_df_sisepuede_industry_fuels.Subsector.unique():
    frac_inen_all_countries.query(f"Country=='{country}' and Subsector =='{subsector}'")[["Product","variable","frac_inen"]]\
                        .pivot(index = 'variable', columns = 'Product', values='frac_inen').plot(kind='bar', stacked=True)
    plt.title(f"Pais : {country}.\nSector : {subsector}")
    plt.show()

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
