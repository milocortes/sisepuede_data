import csv
import pandas as pd
import glob
from iso_countries_faltan import correspondencias_iso_code3

archivos = glob.glob("csv_files/*.csv")
archivos.sort()

df_all_fuels = []
archivos_fail = []

for file_name in archivos:
    print(file_name.split("/")[1])

    try:
        mycsv = csv.reader(open(file_name)) 
        file_name = file_name.split("/")[1]
        raw_data_tab_erp = []  

        for idx, row in enumerate(mycsv): 
            if idx == 9: 
                nombre_columnas_tab_erp = ["Fuel"]+list(row[3:-2]) 
            elif idx in list(range(10,22)):
                raw_data_tab_erp.append(row[2:-2]) 

        df_efficient_vs_retail_price = pd.DataFrame(raw_data_tab_erp, columns=nombre_columnas_tab_erp) 
        df_efficient_vs_retail_price["country"] = file_name.split("-")[0] 
        df_efficient_vs_retail_price["year"] = file_name.split("-")[1].split(".")[0] 

        df_all_fuels.append(df_efficient_vs_retail_price)
    except:
        print("Problemas de lectura")
        archivos_fail.append(file_name)

df_all_fuels = pd.concat(df_all_fuels, ignore_index = True)
sin_iso_code3 = list(set([f for f in df_all_fuels["country"] if len(f)!=3]))

df_all_fuels["country"] = df_all_fuels["country"].replace({nombre : nombre.replace("_", " ") for nombre in sin_iso_code3})
df_all_fuels["country"] = df_all_fuels["country"].replace(correspondencias_iso_code3)

# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]
iso3_m49_correspondence = iso3_m49_correspondence.rename(columns = {"Nation":"country"})

df_all_fuels.rename(columns = {"country":"iso_code3"}, inplace = True)
df_all_fuels = df_all_fuels.merge(right = iso3_m49_correspondence, how = "inner", on = "iso_code3")
acomoda_columnas = list(df_all_fuels.columns[-3:]) + list(df_all_fuels.columns[:-3])
df_all_fuels = df_all_fuels[acomoda_columnas]

long_format_df_fuels = pd.melt(df_all_fuels, id_vars=["iso_code3", "country", "year", "Fuel", "Unit"] ) 

#d#f_all_fuels["tiene_iso"] = df_all_fuels["country"].apply(lambda x: 1 if len(x)==3 else 0)
df_all_fuels.to_csv("output/fuel_subsidies_wide_format.csv", index = False)

#long_format_df_fuels["tiene_iso"] = long_format_df_fuels["country"].apply(lambda x: 1 if len(x)==3 else 0)
long_format_df_fuels.to_csv("output/fuel_subsidies_long_format.csv",  index = False)
