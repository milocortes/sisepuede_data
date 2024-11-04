import pandas as pd 
import os 
from typing import List 
import matplotlib.pyplot as plt 
import numpy as np 


def build_path(PATH : List[str]) -> str:
    return os.path.abspath(os.path.join(*PATH))

FILE_PATH = os.getcwd()
GEORGIA_RD_PATH = build_path([FILE_PATH,  "real_data.csv"])

df = pd.read_csv(GEORGIA_RD_PATH)

## cargamos datos gdp y pop
GDP_POP_PATH = build_path([FILE_PATH, "sectoral_files", "LTGMPC_Baseline_Results.xlsx"])

gdp = pd.read_excel(GDP_POP_PATH).iloc[:-2].drop(columns = ["Source"])

gdp_long = gdp.set_index("Georgia").T

## Retropola población
pop_ssp = df[["Year", "population_gnrl_rural", "population_gnrl_urban"]]
pop_ssp["total_pop"] = pop_ssp[["population_gnrl_rural", "population_gnrl_urban"]].sum(axis=1)
pop_ssp = pop_ssp.drop(columns = ["population_gnrl_rural", "population_gnrl_urban"])

growth_rates_2015_2024 = pop_ssp.set_index("Year").pct_change().loc[2016:2024].total_pop.to_list()
growth_rates_2015_2024.reverse()

growth_rates_2015_2024[3] = growth_rates_2015_2024[2]

pop_wm_2024 = gdp_long.loc[2024]["Population"]

def retropola_pop(valor_inicial, tasas):
    valor_inicial_scope = valor_inicial
    for r in tasas:
        valor_inicial_scope = (1/(1+r))*valor_inicial_scope
        yield valor_inicial_scope

pop_retropolada = [i for i in retropola_pop(pop_wm_2024, growth_rates_2015_2024)]
pop_retropolada.reverse()

df_to_update = pd.DataFrame({"year" : range(2015, 2051),
                            "poblacion" : pop_retropolada + gdp_long["Population"].to_list(),
                            "gdp_growth_rate" : df[["Year", "gdp_mmm_usd"]].set_index("Year").pct_change().loc[:2023].gdp_mmm_usd.to_list() + gdp_long["Real GDP growth rate"].to_list()
                            }
                            )

def extrapola_gdp(valor_inicial, tasas):
    valor_inicial_scope = valor_inicial
    for r in tasas:
        valor_inicial_scope = (1+r)*valor_inicial_scope
        yield valor_inicial_scope

ssp_original_gdp = df["gdp_mmm_usd"].to_list()
gdp_extrapolado = [i for i in extrapola_gdp(ssp_original_gdp[0], df_to_update.iloc[1:]["gdp_growth_rate"])]


## Checa gdp
plt.plot(ssp_original_gdp, label = "gdp ssp")
plt.plot([ssp_original_gdp[0]] + gdp_extrapolado, label = "gdp extrapolado")
plt.legend()
plt.show()

## Agrega gdp
df["gdp_mmm_usd"] = [ssp_original_gdp[0]] + gdp_extrapolado

## Checa población
plt.plot(pop_ssp["total_pop"], label = "poblacion ssp")
plt.plot(df_to_update["poblacion"], label = "poblacion retropolado")
plt.legend()
plt.show()

## Razones poblacion urbana y rural en ssp
razones_pop_ssp = df[["population_gnrl_rural", "population_gnrl_urban"]]/df[["population_gnrl_rural", "population_gnrl_urban"]].sum(axis=1).to_numpy()[:, np.newaxis]

## Actualizamos poblaciones
df[["population_gnrl_rural", "population_gnrl_urban"]] = razones_pop_ssp*df_to_update["poblacion"].to_numpy()[:, np.newaxis]

plt.plot(df[["population_gnrl_rural", "population_gnrl_urban"]].sum(axis = 1).to_numpy(), label = "poblacion ssp")
plt.plot(df_to_update["poblacion"], label = "poblacion retropolado")
plt.legend()
plt.show()

## Guardamos el dataframe de datos de entrada

df[['ef_enfu_combustion_tonne_co2_per_tj_fuel_hydropower', 'ef_enfu_stationary_combustion_tonne_ch4_per_tj_fuel_hydropower', 'ef_enfu_stationary_combustion_tonne_n2o_per_tj_fuel_hydropower']] = 0.0
df.to_csv("real_data.csv", index = False)