import pandas as pd 
import os
import sys 

sisepuede_var = sys.argv[1]

# Definimos rutas

data_path = "../raw_data"

# Definimos nombres de archivos
fao_data_file_name = "FAOSTAT_data_7-6-2022.csv"

# Cargamos datos

fao_data = pd.read_csv(os.path.join(data_path, fao_data_file_name))

# Homologamos nombres de paises

fao_isocode3_cw = {'Türkiye' : 'Turkey', 
                   'United Kingdom of Great Britain and Northern Ireland' : 'United Kingdom', 
                   'Sudan (former)' : 'Sudan',
                   "China, mainland" : "China"}

fao_data["Area"] = fao_data["Area"].replace(fao_isocode3_cw)  

m49_fao_countries = pd.read_json("https://data.apps.fao.org/catalog/dataset/1712bf04-a530-4d55-bb66-54949213985f/resource/b0c1d224-23ea-425d-b994-e15f76feb26b/download/m49-countries.json")

# Agregamos el ISO CODE 3 para todos los paises
cw_fao_names_iso_code3 = {i:j for i,j in zip(m49_fao_countries["country_name_en"], m49_fao_countries["ISO3"])}
cw_fao_names_iso_code3['South Sudan'] = "SSD"
cw_fao_names_iso_code3['China, Taiwan Province of'] = "TWN"

fao_data["iso_code3"] = fao_data["Area"].replace(cw_fao_names_iso_code3)
#fao_data["iso_code3"].unique()

# Cargamos el crosswalk entre Items de FAO ---> sisepuede
cw = pd.read_csv("https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/data_crosswalks/fao_crop_categories.csv")
cw = cw.rename(columns = {"fao_crop" : "Item", "``$CAT-AGRICULTURE$``" : "sisepuede_item"})

cw_fao_item_sisepuede_item = { i:j for i,j in zip(cw["Item"], cw["sisepuede_item"])}

# 30
fao_data["sisepuede_item"] = fao_data["Item"].replace(cw_fao_item_sisepuede_item)

fao_data = fao_data.query("Item != 'Maté'")
fao_data.groupby(["Area","Year","sisepuede_item"])["Value"].mean()

fao_data = fao_data.groupby(["iso_code3", "Area","Year","sisepuede_item"])["Value"].mean().reset_index() 

fao_data["sisepuede_item"] = fao_data["sisepuede_item"].apply(lambda x : f"yf_agrc_{x}_tonne_ha")     

fao_data = fao_data.pivot(index=['iso_code3', 'Area', 'Year'], columns='sisepuede_item', values='Value').reset_index()  

fao_data = fao_data.rename(columns = {"Area" : "Nation"})

## Hacemos interpolación para cubrir los datos faltantes
## Y guardamos datos históricos

path_historical_data = "../input_to_sisepuede/historical"

for sise_var in [i for i in fao_data.columns if "yf_agrc" in i]:

    if sisepuede_var == sise_var:

        if fao_data[sise_var].isna().any():   
            #print(f"{sise_var}    Tiene NaN")
            fao_data[sise_var] = fao_data.groupby(["Nation"])[sise_var].apply(lambda x: x.interpolate().fillna(method='bfill')).reset_index()[sise_var].fillna(0)


        fao_data[["iso_code3","Nation", "Year",sise_var]].to_csv(os.path.join(path_historical_data,f"{sise_var}.csv"), index = False)

## Datos proyectados. El último año lo tomamos como constante para hasta 2050
max_year = fao_data.Year.max()

fao_data = fao_data.query(f"Year=={max_year}")

fao_data = fao_data.drop(columns = "Year")

df_year = pd.DataFrame({"Year" : range(max_year+1, 2051)})
fao_data_projected = fao_data.merge(df_year, how = "cross") 

path_projected_data = "../input_to_sisepuede/projected"

for sise_var in [i for i in fao_data.columns if "yf_agrc" in i]:
    if sisepuede_var == sise_var:
        fao_data_projected[["iso_code3","Nation", "Year",sise_var]].to_csv(os.path.join(path_projected_data,f"{sise_var}.csv"), index = False)

