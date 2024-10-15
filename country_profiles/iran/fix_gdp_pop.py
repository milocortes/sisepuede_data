import pandas as pd 
import os 
from typing import List 
import matplotlib.pyplot as plt 
import numpy as np 


def build_path(PATH : List[str]) -> str:
    return os.path.abspath(os.path.join(*PATH))

FILE_PATH = os.getcwd()
IRAN_RD_PATH = build_path([FILE_PATH,  "real_data.csv"])

df = pd.read_csv(IRAN_RD_PATH)

## cargamos datos gdp y pop
GDP_POP_PATH = build_path([FILE_PATH, "sectoral_files", "Iran macro outputs for CCDR phase 1 energy subsidies.xlsx"])

gdp = pd.read_excel(GDP_POP_PATH, skiprows=2).rename(columns={"Unnamed: 0" : "field"})

gdp_long = gdp.set_index("field").T.loc[2015:]

## Checa gdp
plt.plot(gdp_long["Nominal GDP (billion US$)"].to_numpy(), label = "iran")
plt.plot(df["gdp_mmm_usd"].to_numpy(), label = "ssp")
plt.legend()
plt.show()

## Agrega gdp
df["gdp_mmm_usd"] = gdp_long["Nominal GDP (billion US$)"].to_numpy()

## Checa población
iran_pop_total = gdp_long["Population (million)"].to_numpy()*1_000
ssp_iran_pop_total = df[["population_gnrl_rural", "population_gnrl_urban"]].sum(axis = 1).to_numpy()

plt.plot(ssp_iran_pop_total, label = "ssp")
plt.plot(iran_pop_total, label = "iran")
plt.legend()
plt.show()

## Razones poblacion urbana y rural en ssp
razones_pop_ssp = df[["population_gnrl_rural", "population_gnrl_urban"]]/ssp_iran_pop_total[:,np.newaxis]

## Actualizamos poblaciones
df[["population_gnrl_rural", "population_gnrl_urban"]] = razones_pop_ssp*iran_pop_total[:, np.newaxis]

## Guardamos el dataframe de datos de entrada
df.to_csv("real_data.csv", index = False)