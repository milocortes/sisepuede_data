import pandas as pd 
import os 
from typing import List 
import matplotlib.pyplot as plt 
import numpy as np 
from scipy.interpolate import UnivariateSpline


def build_path(PATH : List[str]) -> str:
    return os.path.abspath(os.path.join(*PATH))

FILE_PATH = os.getcwd()
IRAN_RD_PATH = build_path([FILE_PATH,  "real_data.csv"])

df = pd.read_csv(IRAN_RD_PATH)

## cargamos datos gdp y pop
GDP_POP_PATH = build_path([FILE_PATH, "sectoral_files", "Iran macro outputs for CCDR phase 1 energy subsidies.xlsx"])

gdp = pd.read_excel(GDP_POP_PATH, skiprows=2).rename(columns={"Unnamed: 0" : "field"})

gdp_long = gdp.set_index("field").T.loc[2015:]

### Actualizamos el GDP para que a partir de 2020 crezca a una tasa del 3% 

gdp_actualizado = [df["gdp_mmm_usd"].iloc[5]]
tasa_crecimiento = 0.03

for i in range(30):
    gdp_actualizado.append(
        gdp_actualizado[-1]*(1+tasa_crecimiento)
    )

gdp_actualizado = list(df["gdp_mmm_usd"].iloc[:5]) + gdp_actualizado

## Suaviza serie

spl = UnivariateSpline(range(36), gdp_actualizado)(range(36))

## Checa gdp
plt.plot(gdp_actualizado, label = "GDP actualizado")
plt.plot(df["gdp_mmm_usd"].to_numpy(), label = "GDP ssp")
plt.plot(spl, label = "GDP suavizado")
plt.legend()
plt.show()

## Agrega gdp
df["gdp_mmm_usd"] = spl

## Checa población
iran_pop_total = gdp_long["Population (million)"].to_numpy()*1_000
iran_pop_total_empty = np.copy(iran_pop_total)
iran_pop_total_empty[[6]] = 88213811.5
iran_pop_suavizado = UnivariateSpline(range(36), iran_pop_total_empty)(range(36))
ssp_iran_pop_total = df[["population_gnrl_rural", "population_gnrl_urban"]].sum(axis = 1).to_numpy()

plt.plot(ssp_iran_pop_total, label = "ssp")
plt.plot(iran_pop_total, label = "iran")
plt.plot(iran_pop_total_empty, label = "iran suavizado")
plt.legend()
plt.show()

## Razones poblacion urbana y rural en ssp
razones_pop_ssp = df[["population_gnrl_rural", "population_gnrl_urban"]]/ssp_iran_pop_total[:,np.newaxis]

## Actualizamos poblaciones
df[["population_gnrl_rural", "population_gnrl_urban"]] = razones_pop_ssp*iran_pop_total[:, np.newaxis]

## Guardamos el dataframe de datos de entrada
df.to_csv("real_data.csv", index = False)