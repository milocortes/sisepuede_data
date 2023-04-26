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

country_eeih_fuel_industries_cw_absolutos = country_eeih_fuel_industries_cw.copy()

### SHARES
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


### ABSOLUTOS

country_eeih_fuel_industries_cw_absolutos_long = country_eeih_fuel_industries_cw_absolutos[["iso_code3", "Nation", "Year","sisepuede_var", "value"]].pivot(index=["iso_code3","Nation","Year"], columns='sisepuede_var', values='value').reset_index()


acumula_reciclados = []

for ssp_var, recycled in industries_correspondence_recycled.items():
    columnas_a_cambiar = [i for i in country_eeih_fuel_industries_cw_absolutos_long.columns if ssp_var in i]
    df_recycled = country_eeih_fuel_industries_cw_absolutos_long[columnas_a_cambiar]

    df_recycled = df_recycled.rename(columns = {i:i.replace(ssp_var, recycled) for i in columnas_a_cambiar})

    acumula_reciclados.append(df_recycled)

df_todo_reciclado = pd.concat(acumula_reciclados, axis = 1)

country_eeih_fuel_industries_cw_absolutos_long = pd.concat([country_eeih_fuel_industries_cw_absolutos_long, df_todo_reciclado], axis = 1)

#print(country_eeih_fuel_industries_cw_long.query("iso_code3=='BRA'")[[i for i in country_eeih_fuel_industries_cw_long.columns if "biomass" in i and "manufac" in i]])
#country_eeih_fuel_industries_cw_long_historical = country_eeih_fuel_industries_cw_long.copy()

## Load Socieconomic Data
request_data_historical = lambda x :  f"https://raw.githubusercontent.com/milocortes/sisepuede_data/main/SocioEconomic/{x}/input_to_sisepuede/historical/{x}.csv"
request_data_projected = lambda x :  f"https://raw.githubusercontent.com/milocortes/sisepuede_data/main/SocioEconomic/{x}/input_to_sisepuede/projected/{x}.csv"

socioeconomic_variables = ["area_gnrl_country_ha", "occrateinit_gnrl_occupancy", "gdp_mmm_usd",  "population_gnrl_rural", "population_gnrl_urban"]

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

def remueve_fuels(cadena : str)-> str:
    for i in fuels_correspondence.keys():
        cadena = cadena.replace(i,"")
    return cadena[:-1]

sisepuede_grupos = list(set([remueve_fuels(i) for i in country_eeih_fuel_industries_cw_long_historical.columns[3:]]))

### Detectamos grupos con k-means
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn import preprocessing

min_max_scaler = preprocessing.MinMaxScaler()

#IEA_socieconomic_data = country_eeih_fuel_industries_cw_long_historical.set_index(var_to_index).merge(right=df_socieconomics.set_index(var_to_index), left_index=True, right_index=True)[socioeconomic_variables]

kmeans_sisepuede_grupos = {}

for grupo in sisepuede_grupos:
    IEA_socieconomic_data = country_eeih_fuel_industries_cw_absolutos_long.set_index(var_to_index)[[i for i in country_eeih_fuel_industries_cw_absolutos_long if grupo in i]].sum(axis=1).reset_index().set_index(var_to_index).merge(right=df_socieconomics.set_index(var_to_index), left_index=True, right_index=True)[socioeconomic_variables + [0]]

    #X = IEA_socieconomic_data.to_numpy() 
    X = IEA_socieconomic_data.reset_index().groupby(["iso_code3","Nation"]).mean()[socioeconomic_variables + [0]].to_numpy()

    X_scaled = min_max_scaler.fit_transform(X)

    kmeans_sisepuede_grupos[grupo] = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(X_scaled)
    
    print(grupo)
    for n_clusters in range(2,10):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto").fit(X_scaled)
        labels = kmeans.labels_


        silhouette_avg = metrics.silhouette_score(X_scaled, labels, metric='euclidean')

    
        print(
            "For n_clusters =",
            n_clusters,
            "The average silhouette_score is :",
            silhouette_avg,
        )
    


##### READ IMPUTED DATA
sources_path_imputed = os.path.abspath(os.path.join(dir_path,"..","raw_data","Complete_IEA")) 

import glob 

iea_imputado = pd.concat([pd.read_csv(i).drop(columns = "Unnamed: 0").set_index(["Nation","iso_code3","Year"]) for i in glob.glob(sources_path_imputed+"/*.csv")], axis = 1).reset_index()



'''
REPETIMOS EL MISMO PROCEDIMIENTO
'''

iea_imputado_long = pd.melt(iea_imputado, id_vars=["iso_code3", "Nation", "Year"], value_vars=iea_imputado.columns[3:] ).rename(columns = {"variable":"Subsector"})

iea_imputado_long["Subsector"] = iea_imputado_long["Subsector"].replace({i :i.replace(" Total (PJ)", "") for i in iea_imputado_long.Subsector.unique()})
# Apply crosswalk to IEA-sisepuede industries

iea_imputado_long_industries_cw = []

for sisepuede_ind, cw_iea_indus_list in industries_correspondence.items():

    partial_iea_imputado_long = []
    for ponderador, iea_industry in cw_iea_indus_list:
        individual_df = iea_imputado_long[iea_imputado_long["Subsector"]==iea_industry]
        print(individual_df.shape)
        individual_df.loc[:,"value"]  = individual_df["value"]*ponderador
        partial_iea_imputado_long.append(individual_df)
    
    partial_iea_imputado_long = pd.concat(partial_iea_imputado_long)
    partial_iea_imputado_long.loc[:,"Subsector"] = sisepuede_ind
    
    partial_iea_imputado_long = partial_iea_imputado_long.groupby(["iso_code3", "Nation", "Subsector",  "Year"]).sum().reset_index()

    iea_imputado_long_industries_cw.append(partial_iea_imputado_long)


iea_imputado_long_industries_cw = pd.concat(iea_imputado_long_industries_cw, ignore_index = True)


iea_imputado_long_industries_cw_short = iea_imputado_long_industries_cw.pivot(index=["iso_code3","Nation","Year"], columns='Subsector', values='value').reset_index()

### Predict group

predict_kmeans_sisepuede_grupos = {}

for grupo in iea_imputado_long_industries_cw_short.columns[3:]:
    IEA_socieconomic_data = iea_imputado_long_industries_cw_short.set_index(var_to_index)[[i for i in iea_imputado_long_industries_cw_short if grupo in i]].sum(axis=1).reset_index().set_index(var_to_index).merge(right=df_socieconomics.set_index(var_to_index), left_index=True, right_index=True)[socioeconomic_variables + [0]]


    #X = IEA_socieconomic_data.to_numpy() 
    X = IEA_socieconomic_data.reset_index().groupby(["iso_code3","Nation"]).mean()[socioeconomic_variables + [0]].to_numpy()
    X_scaled = min_max_scaler.fit_transform(X)

    predict_kmeans_sisepuede_grupos[f"frac_inen_energy_{grupo}"] = kmeans_sisepuede_grupos[f"frac_inen_energy_{grupo}"].predict(X_scaled)


predict_iea_group = pd.concat([IEA_socieconomic_data.reset_index()[["iso_code3", "Nation","Year"]].groupby(["iso_code3","Nation"]).mean().reset_index(), 
                                pd.DataFrame(predict_kmeans_sisepuede_grupos) ],axis = 1)


## APLICA EL PROMEDIO 

promedios_sisepuede_grupos = {}

for grupo in sisepuede_grupos:

    promedios_sisepuede_grupos[grupo] = {}

    IEA_socieconomic_data = country_eeih_fuel_industries_cw_long_historical.set_index(var_to_index)[[i for i in country_eeih_fuel_industries_cw_long_historical.columns if grupo in i]].reset_index().set_index(var_to_index).merge(right=df_socieconomics.set_index(var_to_index), left_index=True, right_index=True)

    
    IEA_socieconomic_data_mean = IEA_socieconomic_data.reset_index().groupby(["iso_code3","Nation"]).mean().reset_index()
    
    paises_grupo_uno = IEA_socieconomic_data_mean["iso_code3"][[bool(i) for i in kmeans_sisepuede_grupos[grupo].labels_]].to_list()
    paises_grupo_dos = IEA_socieconomic_data_mean["iso_code3"][[not bool(i) for i in kmeans_sisepuede_grupos[grupo].labels_]].to_list()

    
    df_grupo_uno = IEA_socieconomic_data.reset_index()[IEA_socieconomic_data.reset_index()["iso_code3"].isin(paises_grupo_uno)].set_index(["iso_code3","Nation"])[["Year"] + [i for i in country_eeih_fuel_industries_cw_long_historical if grupo in i]].groupby("Year").mean()
    df_grupo_dos = IEA_socieconomic_data.reset_index()[IEA_socieconomic_data.reset_index()["iso_code3"].isin(paises_grupo_dos)].set_index(["iso_code3","Nation"])[["Year"] + [i for i in country_eeih_fuel_industries_cw_long_historical if grupo in i]].groupby("Year").mean()


    # Renormaliza

    df_grupo_uno_melt = pd.melt(df_grupo_uno.reset_index(), id_vars=["Year"], value_vars=df_grupo_uno.columns)
    df_grupo_uno_melt["value"] = df_grupo_uno_melt.groupby(["Year"])["value"].transform(lambda x: x/x.sum())

    df_grupo_dos_melt = pd.melt(df_grupo_dos.reset_index(), id_vars=["Year"], value_vars=df_grupo_dos.columns)
    df_grupo_dos_melt["value"] = df_grupo_dos_melt.groupby(["Year"])["value"].transform(lambda x: x/x.sum())


    df_grupo_dos = df_grupo_dos_melt.pivot(index='Year', columns='variable', values='value')
    df_grupo_uno = df_grupo_uno_melt.pivot(index='Year', columns='variable', values='value')

    promedios_sisepuede_grupos[grupo][1] = df_grupo_uno
    promedios_sisepuede_grupos[grupo][0] = df_grupo_dos

                
# Imputa valor

acumula_todos_paises = []

for sisepuede_group in predict_iea_group.columns[3:]:
    paises_primer_grupo = predict_iea_group.query(f"{sisepuede_group}==1")[["iso_code3","Nation"]]
    paises_segundo_grupo = predict_iea_group.query(f"{sisepuede_group}==0")[["iso_code3","Nation"]]

    paises_segundo_grupo = paises_segundo_grupo.merge(right=promedios_sisepuede_grupos[sisepuede_group][0].reset_index(), how = "cross")
    paises_primer_grupo = paises_primer_grupo.merge(right=promedios_sisepuede_grupos[sisepuede_group][1].reset_index(), how = "cross")

    
    todos_grupos = pd.concat([paises_primer_grupo, paises_segundo_grupo], ignore_index = True)
    acumula_todos_paises.append(todos_grupos.set_index(["iso_code3","Nation","Year"]))

imputados_paises = pd.concat(acumula_todos_paises, axis =1).reset_index()

acumula_reciclados = []

for ssp_var, recycled in industries_correspondence_recycled.items():
    columnas_a_cambiar = [i for i in imputados_paises.columns if ssp_var in i]
    df_recycled = imputados_paises[columnas_a_cambiar]

    df_recycled = df_recycled.rename(columns = {i:i.replace(ssp_var, recycled) for i in columnas_a_cambiar})

    acumula_reciclados.append(df_recycled)

df_todo_reciclado = pd.concat(acumula_reciclados, axis = 1)

imputados_paises = pd.concat([imputados_paises, df_todo_reciclado], axis = 1)

imputados_paises = imputados_paises[~imputados_paises["iso_code3"].isin(country_eeih_fuel_industries_cw_long_historical.iso_code3.unique())]

country_eeih_fuel_industries_cw_long_historical = pd.concat([country_eeih_fuel_industries_cw_long_historical, imputados_paises], ignore_index = True)
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