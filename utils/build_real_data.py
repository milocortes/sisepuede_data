import pandas as pd
from tqdm import tqdm
import glob
from datetime import datetime
import sys 

# Cargamos programas de SSP
# Cargamos la ruta del sisepuede para hacer uso de algunas utilerías
SSP_PYTHON_PATH = '/opt/sisepuede/python'
sys.path.append(SSP_PYTHON_PATH)
import define_transformations_integrated as dtr
import sisepuede as ssp
import setup_analysis as sa
import support_classes as sc    
import sisepuede_file_structure as sfs
import support_functions as sf

# Usamos utilerias para obtener información de los países
file_struct = sfs.SISEPUEDEFileStructure()
model_attributes = file_struct.model_attributes
regions = sc.Regions(model_attributes)

regions_table = regions.attributes.table.copy()

iso2region = {i:j for i,j in regions_table[["iso_alpha_3", "region"]].to_records(index = False)}
region2iso = {i:j for i,j in regions_table[["region", "iso_alpha_3"]].to_records(index = False)}

# Sectores a procesar
sisepuede_sector = ["AFOLU", "CircularEconomy", "IPPU", "SocioEconomic", "Energy"]

var_to_index = ["iso_code3", "Year"]

country = region2iso[sys.argv[1]]

countries = []
countries.append(country)
total_countries = len(countries)

acumula_countries = []

for idx, country in enumerate(countries):
    print(f"#{idx}/{total_countries} - {country}")
    acumula_files = []
    for sector in sisepuede_sector:

        historical_subsector_files = [i for i in glob.glob(f"/opt/sisepuede_data/{sector}/*/*/*/*.csv") if "historical"  in i] 
        projected_subsector_files = [i for i in glob.glob(f"/opt/sisepuede_data/{sector}/*/*/*/*.csv") if "projected"  in i]

        print(sector)
        for historical_file, projected_file in tqdm(zip(historical_subsector_files, projected_subsector_files)):

            historical_df = pd.read_csv(historical_file)
            projected_df = pd.read_csv(projected_file)

            historical_df = historical_df.rename(columns = {"location_code" : "iso_code3", "ISO3":"iso_code3", "year" : "Year"})
            projected_df = projected_df.rename(columns = {"location_code" : "iso_code3", "ISO3":"iso_code3", "year" : "Year"})

            historical_df = historical_df.query(f"iso_code3=='{country}'").reset_index(drop=True)
            projected_df = projected_df.query(f"iso_code3=='{country}'").reset_index(drop=True)

            historical_df["Year"] = historical_df["Year"].astype(int)
            projected_df["Year"] = projected_df["Year"].astype(int)

            sisepuede_var_name = [i for i in historical_df.columns if len(i.split("_")) > 2][0] 

            merge_df_sisepuede = pd.concat([historical_df[["iso_code3","Year",sisepuede_var_name]], projected_df[["iso_code3","Year",sisepuede_var_name]]])

            merge_df_sisepuede = merge_df_sisepuede.sort_values(["iso_code3", "Year"])

            merge_df_sisepuede = merge_df_sisepuede.set_index(var_to_index)

            merge_df_sisepuede = merge_df_sisepuede.loc[~merge_df_sisepuede.index.duplicated(keep='first')]

            merge_df_sisepuede = merge_df_sisepuede.query("Year >=2015 and Year<=2050")
            acumula_files.append(merge_df_sisepuede)

    real_data = pd.concat(acumula_files, axis = 1).reset_index()

    fake_data_complete = pd.read_csv("https://raw.githubusercontent.com/jcsyme/sisepuede/main/ref/fake_data/fake_data_complete.csv")
    fake_data_complete = fake_data_complete[list(set(fake_data_complete.columns) - set(real_data.columns)) ]

    mix_data = pd.concat([real_data, fake_data_complete], axis = 1)

    acumula_countries.append(mix_data)

all_mix_data = pd.concat(acumula_countries, ignore_index = True)

today_date = str( datetime.now())[:10].replace("-","")

all_mix_data.to_csv(f"/opt/ssp_input_data/real_data.csv", index = False)
