import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools

import sys 
import os 

sisepuede_var = sys.argv[1]
#sisepuede_var = "frac_trns_fuelmix_public_biofuels"

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" )) 

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

# Get data from EEIH
eeih = pd.read_csv(os.path.join(sources_path, "IEA_transport_energy.csv"))

eeih.Product = eeih.Product.str.strip()
# Load WB regionalization
wb_reg = pd.read_csv(os.path.join(sources_path, "wb_regionalization.csv"))

eeih.rename(columns = {"Country" : "Nation"}, inplace = True)

eeih = eeih.merge(right=wb_reg, how = "inner", on = "Nation")

# Melt data
country_eeih = eeih.melt(id_vars = wb_reg.columns.to_list() + eeih.columns[1:3].to_list())

# Replace ".." for np.nan
country_eeih["value"] = country_eeih["value"].replace("..", np.nan)
country_eeih.value = country_eeih.value.astype(float)

country_eeih = country_eeih[["iso_code3", "Nation"] + eeih.columns[1:3].to_list() + ["variable", "value"]]


# Apply crosswalk
crosswalk = {
        "biofuels": ("Other sources (PJ)", ),
        "diesel": ("Diesel and light fuel oil (PJ)", ),
        "electricity": ("Electricity (PJ)", ),
        "gasoline": ("Motor gasoline (PJ)", ),
        "hydrocarbon_gas_liquids": ("LPG (PJ)", ),
        "hydrogen": 0,
        "kerosene": ("Jet fuel and aviation gasoline (PJ)", ),
        "natural_gas": ("Gas (PJ)", ),
        "oil": ("Heavy fuel oil (PJ)", )
    }

country_eeih["Product"] = country_eeih["Product"].replace({v[0] : k for k,v in crosswalk.items() if k!='hydrogen'})

country_eeih = country_eeih[country_eeih["Product"].isin([i for i in crosswalk if i!="hydrogen"])]

# Interpolate missing year
country_eeih.variable = country_eeih.variable.astype(int)
missing_years = list(set(range(min(country_eeih.variable),max(country_eeih.variable)+1)) - set(country_eeih.variable.unique()))
missing_years.sort()

acumula_df = []
for my in missing_years:
    parcial_country_eeih = country_eeih.query("variable == 2000")
    parcial_country_eeih.loc[:,"value"] = np.nan
    parcial_country_eeih.loc[:,"variable"] = my

    acumula_df.append(parcial_country_eeih)

df_missing_years = pd.concat(acumula_df, ignore_index = True)

country_eeih = pd.concat([country_eeih, df_missing_years], ignore_index = True)

country_eeih = country_eeih.sort_values(["Nation", "Product", "variable"]).reset_index(drop = True)

country_eeih.loc[:, "value"] = country_eeih.groupby(["Nation", "Product"])["value"].apply(lambda x: x.interpolate().fillna(method='bfill')).reset_index()["value"]


## Specific fuel by sisepuede_variable
fuelmix_passenger_freight = {"frac_trns_fuelmix_public" : ["biofuels", "diesel" , "electricity", "gasoline", "hydrogen", "natural_gas"],
"frac_trns_fuelmix_road_heavy_freight" : ["biofuels", "diesel" , "electricity", "gasoline", "hydrogen", "natural_gas"],
"frac_trns_fuelmix_road_heavy_regional" : ["biofuels", "diesel" , "electricity", "gasoline", "hydrogen", "natural_gas"],
"frac_trns_fuelmix_road_light" : ["biofuels", "diesel" , "electricity", "gasoline", "hydrogen"]}

## Select group to be defined
fuel_mix_group = [i for i in fuelmix_passenger_freight if i in sisepuede_var][0]

## Load Socieconomic Data
import numpy as np
from sklearn.linear_model import LinearRegression

request_data_historical = lambda x :  f"https://raw.githubusercontent.com/milocortes/sisepuede_data/main/SocioEconomic/{x}/input_to_sisepuede/historical/{x}.csv"
request_data_projected = lambda x :  f"https://raw.githubusercontent.com/milocortes/sisepuede_data/main/SocioEconomic/{x}/input_to_sisepuede/projected/{x}.csv"

socioeconomic_variables = ["area_gnrl_country_ha", "occrateinit_gnrl_occupancy", "gdp_mmm_usd",  "population_gnrl_rural", "population_gnrl_urban"]
#socioeconomic_variables = [ "gdp_mmm_usd",  "population_gnrl_rural", "population_gnrl_urban"]
#socioeconomic_variables = ["gdp_mmm_usd"]
#socioeconomic_variables = ["area_gnrl_country_ha", "gdp_mmm_usd"]

posibles_combinaciones = []

for i in range(1, len(socioeconomic_variables)):
    posibles_combinaciones.extend(list(itertools.combinations(socioeconomic_variables, i)))

posibles_combinaciones.append(socioeconomic_variables[:])

var_to_index = ["iso_code3", "Nation", "Year"]


def request_sisepuede_var(sisepuede_variable):
    historical_df = pd.read_csv(request_data_historical(sisepuede_variable))
    projected_df = pd.read_csv(request_data_projected(sisepuede_variable))

    merge_df_sisepuede = pd.concat([historical_df, projected_df])

    merge_df_sisepuede = merge_df_sisepuede.sort_values(["iso_code3", "Year"])

    #merge_df_sisepuede = merge_df_sisepuede.drop_duplicates() 
    merge_df_sisepuede = merge_df_sisepuede.set_index(var_to_index)

    merge_df_sisepuede = merge_df_sisepuede.loc[~merge_df_sisepuede.index.duplicated(keep='first')]

    return merge_df_sisepuede



dfs_socieconomics = [request_sisepuede_var(i) for i in socioeconomic_variables]

df_socieconomics = pd.concat(dfs_socieconomics, axis = 1).sort_values(var_to_index)
df_socieconomics = df_socieconomics.drop(columns = "Unnamed: 0")
df_socieconomics = df_socieconomics.reset_index()
df_socieconomics = df_socieconomics.dropna()


## Merg with iea data
country_eeih.rename(columns = {"variable" : "Year"}, inplace = True)

## Run a regression for each fuel type

acumula_df_imputed_fuel_type = []
acumula_best_coefs = []

for fuel_type in fuelmix_passenger_freight[fuel_mix_group]:
#for fuel_type in crosswalk.keys():

    if fuel_type != "hydrogen":
        print(fuel_type)

        fuel_type_data = country_eeih.query(f"Product=='{fuel_type}'")

        regress_data = fuel_type_data[var_to_index+["value"]].set_index(var_to_index).merge(right=df_socieconomics.set_index(var_to_index), left_index=True, right_index=True)

        acumula = {}

        for conjunto in posibles_combinaciones:
            y = regress_data["value"].to_numpy()
            X = regress_data[list(conjunto)].to_numpy()

            reg = LinearRegression(fit_intercept = False).fit(X, y)
            acumula[tuple(conjunto)] = (reg.coef_, reg.score(X,y))

        acumula = {k : v for k,v in acumula.items() if all(v[0] > 0)}

        var_names, (best_coefs, best_score) = sorted(acumula.items(), key = lambda x:x[1][1])[-1]

        acumula_best_coefs.append(( fuel_type,var_names,best_score))

        df_socieconomics_to_project = df_socieconomics[~df_socieconomics["iso_code3"].isin(country_eeih["iso_code3"].unique())]
        df_socieconomics_minimal = df_socieconomics_to_project[["iso_code3", "Nation", "Year"]]
        df_socieconomics_minimal.loc[:, ["Product"] ] = fuel_type

        X = regress_data[list(var_names)].to_numpy()

        reg = LinearRegression(fit_intercept = False).fit(X, y)

        X_to_project = df_socieconomics_to_project[list(var_names)].to_numpy()
        df_socieconomics_minimal.loc[:, ["value"] ] = reg.predict(X_to_project)
        acumula_df_imputed_fuel_type.append(df_socieconomics_minimal)

## Agrupamos los datos imputados
df_imputed_fuel_type = pd.concat(acumula_df_imputed_fuel_type, ignore_index = True)

## Definimos que los datos proyectados son igual al último dato histórico para los países no imputados
acumula_historicos_proyectados = []

for i in range(max(country_eeih.Year)+1, 2050 + 1):
    partial_country_eeih = country_eeih.query(f"Year=={max(country_eeih.Year)}")
    partial_country_eeih.loc[:,["Year"]] = i

    acumula_historicos_proyectados.append(partial_country_eeih)

df_country_proyectados = pd.concat(acumula_historicos_proyectados, ignore_index = True)

## Agrupamos históricos y proyectados
country_eeih = pd.concat([country_eeih, df_country_proyectados], ignore_index = True)

## Agrupamos datos reales e imputados
df_fuel_type = pd.concat([country_eeih[["iso_code3", "Nation", "Product", "Year", "value"]], df_imputed_fuel_type], ignore_index = True)

## Subset only fuels in fuel_mix_group
df_fuel_type = df_fuel_type[df_fuel_type["Product"].isin(fuelmix_passenger_freight[fuel_mix_group])]

df_fuel_type["share"] = df_fuel_type.groupby( df_fuel_type.columns[:-3].to_list() + ["Year"])["value"].transform(lambda x: x/x.sum())

"""
brazil = df_fuel_type[df_fuel_type["iso_code3"] == "CRI"]
brazil.set_index("Year", inplace=True)
brazil.groupby('Product')['share'].plot(title = "Costa Rica\nTransport - Energy", legend=True)
plt.show()
"""
df_fuel_type = df_fuel_type.drop(columns = "value")
df_fuel_type["Product"] = df_fuel_type["Product"].apply(lambda x : f"{fuel_mix_group}_{x}")

long_df_fuel_type = df_fuel_type.pivot_table(values = "share", index = ["iso_code3", "Nation", "Year"], columns = "Product").reset_index()

## Falta hidrógeno?
fuel_mix_actual_columns = [i for i in long_df_fuel_type.columns if fuel_mix_group in i]

if len(fuel_mix_actual_columns) != len(fuelmix_passenger_freight[fuel_mix_group]):
    long_df_fuel_type[f"{fuel_mix_group}_hydrogen"] = 0.0



## Save historical data
save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 
save_path_historical_file = os.path.join(save_path_historical, f"{sisepuede_var}.csv") 

historical_data = long_df_fuel_type[["iso_code3", "Nation", "Year", sisepuede_var]].query("Year<=2020")

historical_data.to_csv(save_path_historical_file, index = False)

## Save historical data
save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))
save_path_projected_file = os.path.join(save_path, "projected", f"{sisepuede_var}.csv") 

projected_data = long_df_fuel_type[["iso_code3", "Nation", "Year", sisepuede_var]].query("Year>2020")
projected_data.to_csv(save_path_projected_file, index = False)