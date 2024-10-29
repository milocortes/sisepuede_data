import pandas as pd 
import numpy as np


df = pd.read_csv("real_data.csv")
frac_inen = pd.read_csv("frac_inen_updated.csv")
frac_inen = frac_inen.iloc[:36]

turquia = pd.read_csv("real_data_turkey.csv")

# Agregamos datos de Sonya al real data

frac_inen = frac_inen.replace(np.nan, 0.0)

#df[[i for i in frac_inen.columns if "frac_inen" in i]] = turquia[[i for i in frac_inen.columns if "frac_inen" in i]]

df[[i for i in frac_inen.columns if "frac_inen" in i]] = frac_inen[[i for i in frac_inen.columns if "frac_inen" in i]]

# Asignaremos el grupo de variables frac_inen_energy_agriculture_and_livestock, frac_inen_energy_cement, frac_inen_energy_glass
# de turquia a los datos de iran

turquia_imputa = ["frac_inen_energy_agriculture_and_livestock", "frac_inen_energy_cement", "frac_inen_energy_glass"]

for ti in turquia_imputa:
    ti_todo = [i for i in turquia.columns if ti in i]
    df[ti_todo] = turquia[ti_todo]


map_reciclado = {"frac_inen_energy_recycled_glass" : "frac_inen_energy_glass",
"frac_inen_energy_recycled_metals" : "frac_inen_energy_metals",
"frac_inen_energy_recycled_paper" : "frac_inen_energy_paper", 
"frac_inen_energy_recycled_plastic" : "frac_inen_energy_plastic",  
"frac_inen_energy_recycled_rubber_and_leather" : "frac_inen_energy_rubber_and_leather", 
"frac_inen_energy_recycled_textiles" : "frac_inen_energy_textiles", 
"frac_inen_energy_recycled_wood" : "frac_inen_energy_wood"}

for k,v in map_reciclado.items():
    vars_normales = [i for i in df.columns if v in i]
    vars_reciclado = [i for i in df.columns if k in i]

    df[vars_reciclado] = df[vars_normales]


df.to_csv("real_data.csv", index = False)

