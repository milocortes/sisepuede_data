import pandas as pd
import matplotlib.pyplot as plt
import os 
import numpy as np 
import sys 

from sectors_assumptions_nidhi_cw import industries_correspondence, fuels_correspondence, industries_correspondence_recycled


sisepuede_var = sys.argv[1]
#sisepuede_var = "frac_trns_fuelmix_public_biofuels"

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

# Set directories
#dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" )) 

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

# Get data from EEIH
eeih = pd.read_csv(os.path.join(sources_path, "iea_industry_energy.csv.bz2"))

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

# Apply crosswalk to fuels
cw_fuels_ssp = []
for k,v in fuels_correspondence.items():
    if isinstance(v,tuple):
        partial_country_eeih = country_eeih.query(f"Product =='{v[1]}'")
        partial_country_eeih["value"] = partial_country_eeih["value"]*v[0]
        partial_country_eeih["Product"] = partial_country_eeih["Product"].replace( {v[1] : k})
        cw_fuels_ssp.append(partial_country_eeih)

country_eeih_fuel_cw = pd.concat(cw_fuels_ssp, ignore_index = True)

# Apply crosswalk to IEA-sisepuede industries

country_eeih_fuel_industries_cw = []

for sisepuede_ind, cw_iea_indus_list in industries_correspondence.items():

    partial_country_eeih_fuel_cw = []
    for ponderador, iea_industry in cw_iea_indus_list:
        individual_df = country_eeih_fuel_cw[country_eeih_fuel_cw["Subsector"]==iea_industry]
        individual_df.loc[:,"value"]  = individual_df["value"]*ponderador
        partial_country_eeih_fuel_cw.append(individual_df)
    
    partial_country_eeih_fuel_cw = pd.concat(partial_country_eeih_fuel_cw)
    partial_country_eeih_fuel_cw.loc[:,"Subsector"] = sisepuede_ind
    
    partial_country_eeih_fuel_cw = partial_country_eeih_fuel_cw.groupby(["iso_code3", "Nation", "Subsector", "Product", "variable"]).sum().reset_index()

    country_eeih_fuel_industries_cw.append(partial_country_eeih_fuel_cw)


country_eeih_fuel_industries_cw = pd.concat(country_eeih_fuel_industries_cw, ignore_index = True)

"""
acumula_verificacion = []

for subsector in country_eeih_fuel_industries_cw.Subsector.unique():
    verifica_calculo = country_eeih_fuel_industries_cw.query(f"Subsector == '{subsector}' and (iso_code3=='BRA' or iso_code3=='MEX') and variable =='2015'").pivot(index=["iso_code3","Nation","Subsector","variable"], columns='Product', values='value').reset_index()
    acumula_verificacion.append(verifica_calculo)


verifica = pd.concat(acumula_verificacion,ignore_index = True)

verifica_melt = pd.melt(verifica, id_vars=["iso_code3", "Nation", "Subsector", "variable"], value_vars=verifica.columns[5:])

verifica.set_index(["iso_code3","Nation","Subsector","variable"]).sum(axis=1).reset_index().query("Nation=='Brazil'").sort_values(["iso_code3","Nation","Subsector"])

verifica_melt["Product"] = verifica_melt["Product"].replace({k:v[1] for k,v in fuels_correspondence.items() if isinstance(v, tuple)})

verifica_melt = verifica_melt.groupby(list(verifica_melt.columns[:-2])).sum().reset_index()

verifica_iea_products = verifica_melt.pivot(index=["iso_code3","Nation","Subsector","variable"], columns='Product', values='value').reset_index()

verifica_iea_products.to_csv("verifica_IEA_industrias_hermilo.csv", index = False)


eeih = pd.read_csv(os.path.join(sources_path, "iea_industry_energy.csv.bz2"))

eeih.Product = eeih.Product.str.strip()

eeih_raw = eeih[["Country", "Subsector", "Product","2015"]]
eeih_raw = eeih_raw.rename(columns = {"2015":"value"})
eeih_raw["variable"] = 2015
eeih_raw["value"] = eeih_raw["value"].replace("..", np.nan)
eeih_raw.value = eeih_raw.value.astype(float)

eeih_raw = eeih_raw[eeih_raw["Country"].isin(["Brazil","Mexico"])]

acumula_eeih_raw = []

for k,v in industries_correspondence.items():
    if len(v)==1:
        partial_eeih_raw = eeih_raw[eeih_raw["Subsector"] == v[0][1]]
        acumula_eeih_raw.append(
            partial_eeih_raw.pivot(index=["Country","Subsector","variable"], columns='Product', values='value')
        )

acumula_eeih_raw = pd.concat(acumula_eeih_raw).reset_index()
"""


country_eeih_fuel_industries_cw["sisepuede_var"] = "frac_inen_energy_" + country_eeih_fuel_industries_cw["Subsector"] + "_" +country_eeih_fuel_industries_cw["Product"]
country_eeih_fuel_industries_cw["variable"] = country_eeih_fuel_industries_cw["variable"].astype(int)
country_eeih_fuel_industries_cw = country_eeih_fuel_industries_cw.rename(columns = {"variable" : "Year"})


country_eeih_fuel_industries_cw["value"] = country_eeih_fuel_industries_cw.groupby(["iso_code3", "Subsector", "Year"])["value"].transform(lambda x: x/x.sum())

country_eeih_fuel_industries_cw.query("Year==2015 and iso_code3=='BRA' and Subsector =='other_product_manufacturing'")

#country_eeih_fuel_industries_cw = country_eeih_fuel_industries_cw[["iso_code3", "Nation", "Year","sisepuede_var", "value"]]
#country_eeih_fuel_industries_cw["value"] = country_eeih_fuel_industries_cw.groupby(["iso_code3", "Nation", "Year"])["value"].transform(lambda x: x/x.sum())

country_eeih_fuel_industries_cw_long = country_eeih_fuel_industries_cw[["iso_code3", "Nation", "Year","sisepuede_var", "value"]].pivot(index=["iso_code3","Nation","Year"], columns='sisepuede_var', values='value').reset_index()

country_eeih_fuel_industries_cw_long = country_eeih_fuel_industries_cw_long.fillna(0)

acumula_reciclados = []

for ssp_var, recycled in industries_correspondence_recycled.items():
    columnas_a_cambiar = [i for i in country_eeih_fuel_industries_cw_long.columns if ssp_var in i]
    df_recycled = country_eeih_fuel_industries_cw_long[columnas_a_cambiar]

    df_recycled = df_recycled.rename(columns = {i:i.replace(ssp_var, recycled) for i in columnas_a_cambiar})

    acumula_reciclados.append(df_recycled)

df_todo_reciclado = pd.concat(acumula_reciclados, axis = 1)

country_eeih_fuel_industries_cw_long = pd.concat([country_eeih_fuel_industries_cw_long, df_todo_reciclado], axis = 1)

#print(country_eeih_fuel_industries_cw_long.query("iso_code3=='BRA'")[[i for i in country_eeih_fuel_industries_cw_long.columns if "biomass" in i and "manufac" in i]])
country_eeih_fuel_industries_cw_long_historical = country_eeih_fuel_industries_cw_long.copy()



###Projected

anios_proyectar = pd.DataFrame({"Year" : range(2021, 2051)})

country_eeih_fuel_industries_cw_long_projected = country_eeih_fuel_industries_cw_long_historical.query("Year==2020").drop(columns = "Year").merge(right=anios_proyectar, how = "cross")
#print(country_eeih_fuel_industries_cw_long_projected.query("iso_code3=='BRA'")[[i for i in country_eeih_fuel_industries_cw_long.columns if "biomass" in i and "manufac" in i]])


## Save historical data
save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 
save_path_historical_file = os.path.join(save_path_historical, f"{sisepuede_var}.csv") 

country_eeih_fuel_industries_cw_long_historical = country_eeih_fuel_industries_cw_long_historical[["iso_code3", "Nation", "Year", sisepuede_var]].query("Year<=2020")

country_eeih_fuel_industries_cw_long_historical.to_csv(save_path_historical_file, index = False)

## Save historical data
save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))
save_path_projected_file = os.path.join(save_path, "projected", f"{sisepuede_var}.csv") 

country_eeih_fuel_industries_cw_long_projected = country_eeih_fuel_industries_cw_long_projected[["iso_code3", "Nation", "Year", sisepuede_var]].query("Year>2020")
country_eeih_fuel_industries_cw_long_projected.to_csv(save_path_projected_file, index = False)