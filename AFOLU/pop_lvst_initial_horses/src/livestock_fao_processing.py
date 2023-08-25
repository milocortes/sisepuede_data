import pandas as pd 
import os

import sys 

sisepuede_var_name = sys.argv[1]

# Definimos rutas

data_path = "../raw_data"

# Definimos nombres de archivos
fao_data_file_name = "FAOSTAT_data_7-4-2022(2).csv"

# Cargamos datos
encode = "ISO-8859-1"

fao_data = pd.read_csv(os.path.join(data_path, fao_data_file_name), encoding = encode)
m49_fao_countries = pd.read_json("https://data.apps.fao.org/catalog/dataset/1712bf04-a530-4d55-bb66-54949213985f/resource/b0c1d224-23ea-425d-b994-e15f76feb26b/download/m49-countries.json")

# Agregamos el ISO CODE 3 para todos los paises
cw_fao_names_iso_code3 = {i:j for i,j in zip(m49_fao_countries["country_name_en"], m49_fao_countries["ISO3"])}
fao_data["iso_code3"] = fao_data["Area"].replace(cw_fao_names_iso_code3)

fao_data["iso_code3"] = fao_data["iso_code3"].replace({'T?rkiye': 'TUR', 'United Kingdom of Great Britain and Northern Ireland' : "GBR"})

# Cargamos el crosswalk entre Items de FAO ---> sisepuede
cw =  pd.read_csv(os.path.join(data_path, "items_classification.csv"))[["Item_Fao", "File_Sisepuede"]]

fao_data = fao_data[fao_data.Item.isin(cw.Item_Fao)]

cw_dict = {i : j for i,j in zip(cw["Item_Fao"], cw["File_Sisepuede"])}

# 30
fao_data["sisepuede_item"] = fao_data["Item"].replace(cw_dict)

fao_data = fao_data.groupby(["iso_code3", "Area","Year","sisepuede_item"])["Value"].mean().reset_index() 

fao_data = fao_data.pivot_table(index=['iso_code3', 'Area', 'Year'], columns='sisepuede_item', values='Value').reset_index()  

fao_data = fao_data.rename(columns = {"Area" : "Nation"})

fao_data["pop_lvst_initial_cattle_dairy"] = fao_data["pop_lvst_initial_cattle_nondairy"].copy()


## Hacemos interpolación para cubrir los datos faltantes
## Y guardamos datos históricos

path_historical_data = "../input_to_sisepuede/historical"

if fao_data[sisepuede_var_name].isna().any():   
    #print(f"{sise_var}    Tiene NaN")
    fao_data[sisepuede_var_name] = fao_data.groupby(["Nation"])[sisepuede_var_name].apply(lambda x: x.interpolate().fillna(method='bfill')).reset_index()[sisepuede_var_name].fillna(0)
    #fao_data[sisepuede_var_name] = fao_data[["Nation",sisepuede_var_name]].groupby(["Nation"])[sisepuede_var_name].apply(lambda x : x.interpolate(method = "spline", order = 1, limit_direction = "both"))
    #fao_data[sisepuede_var_name] = fao_data[["Nation",sisepuede_var_name]].groupby(["Nation"])[sisepuede_var_name].apply(lambda x: x.interpolate(order = 1, limit_direction = "both").fillna(method='bfill')).reset_index()[sisepuede_var_name].fillna(0)

fao_data[["iso_code3","Nation", "Year",sisepuede_var_name]].to_csv(os.path.join(path_historical_data,f"{sisepuede_var_name}.csv"), index = False)

## Datos proyectados. El último año lo tomamos como constante para hasta 2050
max_year = fao_data.Year.max()

fao_data = fao_data.query(f"Year=={max_year}")

fao_data = fao_data.drop(columns = "Year")

df_year = pd.DataFrame({"Year" : range(max_year+1, 2051)})
fao_data_projected = fao_data.merge(df_year, how = "cross") 

path_projected_data = "../input_to_sisepuede/projected"

fao_data_projected[["iso_code3","Nation", "Year",sisepuede_var_name]].to_csv(os.path.join(path_projected_data,f"{sisepuede_var_name}.csv"), index = False)