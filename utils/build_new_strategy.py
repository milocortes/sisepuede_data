import sys

# Cargamos la ruta del sisepuede para hacer uso de algunas utilerías
SSP_PYTHON_PATH = '/opt/sisepuede/python'
sys.path.append(SSP_PYTHON_PATH)

# Cargamos paquetes
import os, os.path
import numpy as np
import pandas as pd
from typing import List, Union

# Cargamos programas de SSP
import define_transformations_integrated as dtr
import sisepuede as ssp
import setup_analysis as sa
import support_classes as sc    
import sisepuede_file_structure as sfs
import support_functions as sf
import subprocess

# Get data from yaml
import yaml

with open('ssp_config_params.yml', 'r') as file:
    ssp_strategy_metadata = yaml.safe_load(file)

tx_function_name = ssp_strategy_metadata["new_strategy_params"]["strategy_function_name"]
tx_code = ssp_strategy_metadata["new_strategy_params"]["strategy_code"]
tx_id = ssp_strategy_metadata["new_strategy_params"]["strategy_id"]
tx_description =  ssp_strategy_metadata["new_strategy_params"]["Description"]
tx_name = ssp_strategy_metadata["new_strategy_params"]["strategy"]
tx_baseline_strategy_id = ssp_strategy_metadata["new_strategy_params"]["baseline_strategy_id"]

strategy_data_to_csv = pd.DataFrame({'strategy_id' : [tx_id] ,
 'strategy' : [tx_name],
 'strategy_code' : [tx_code],
 'baseline_strategy_id' : [tx_baseline_strategy_id],
 'Description' : [tx_description]
 }
)


# Usamos utilerias para obtener información de los países
file_struct = sfs.SISEPUEDEFileStructure()
model_attributes = file_struct.model_attributes
regions = sc.Regions(model_attributes)

regions_table = regions.attributes.table.copy()

iso2region = {i:j for i,j in regions_table[["iso_alpha_3", "region"]].to_records(index = False)}
region2iso = {i:j for i,j in regions_table[["region", "iso_alpha_3"]].to_records(index = False)}


# Definimos variables
year_0_ramp = 2025
dir_calibs = "/opt/ssp_input_data"
fp_inputs = os.path.join(dir_calibs, "real_data.csv")
df_input = pd.read_csv(fp_inputs)
field_region = "nation"

# Agregamos la columna nation
df_input["nation"] = df_input["iso_code3"].replace(iso2region)

regions_run = list(set(df_input["nation"]))

# reduce inputs
df_input = df_input[
    df_input[field_region].isin(regions_run)
].reset_index(drop = True)

# set some parameters (WILL SET TO READ FROM A CONFIG OR STRATEGY DEFINITION FILE)
dict_config_te = {
    "categories_entc_max_investment_ramp": [
        "pp_hydropower",
        "pp_nuclear"
    ],
    "categories_entc_renewable": [
        "pp_geothermal",
        "pp_hydropower",
        "pp_ocean",
        "pp_solar",
        "pp_wind"
    ],
    "categories_inen_high_heat": [
        "cement",
        "chemicals",
        "glass",
        "lime_and_carbonite",
        "metals"
    ],
    "dict_entc_renewable_target_msp": {
        "pp_solar": 0.15,
        "pp_geothermal": 0.1,
        "pp_wind": 0.15
    },
    "frac_inen_high_temp_elec_hydg": 0.5*0.45,
    "frac_inen_low_temp_elec": 0.95*0.45,
    "n_tp_ramp": None,
    "vir_renewable_cap_delta_frac": 0.01,
    "vir_renewable_cap_max_frac": 0.1,
    "year_0_ramp": year_0_ramp
}

transformations_integrated = dtr.TransformationsIntegrated(
    dict_config_te,
    df_input = df_input,
    field_region = field_region,
    regions = regions_run,
)

### Definimos las transformaciones a aplicar
transformaciones_activas = ssp_strategy_metadata["new_strategy_params"]["transformaciones_activas"]


tx_afolu = [i for i in dir(transformations_integrated.transformations_afolu) if i.startswith("transformation")]
tx_ce = [i for i in dir(transformations_integrated.transformations_circular_economy) if i.startswith("transformation")]
tx_energy = [i for i in dir(transformations_integrated.transformations_energy) if i.startswith("transformation")]
tx_ippu = [i for i in dir(transformations_integrated.transformations_ippu) if i.startswith("transformation")]


transformation_by_sector = {
    "transformations_afolu" :  tx_afolu,
    "transformations_ce" :  tx_ce,
    "transformations_energy" :  tx_energy,
    "transformations_ippu" :  tx_ippu

}

lista_transformaciones = [
    [f"self.{i}.{k}" for i,j in transformation_by_sector.items() for k in j if transformations_integrated.dict_transformations[tx_class.id].function.__name__ in k][0]
     for tx_code,tx_class in transformations_integrated.dict_transformations.items() if tx_class.code in transformaciones_activas
]

import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Definimos la configuración de jinja
file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)

# Cargamos el template
template_ssp_strategy = env.get_template('templates/template_strategy_ssp')

# Enviamos la lista de tablas al template
output_tables = template_ssp_strategy.render(tx_function_name = tx_function_name,
                                             tx_code = tx_code,
                                             lista_transformaciones = lista_transformaciones)

with open("strategy_ssp.txt", "w") as text_file:
    text_file.write(output_tables)

# Actualizamos csv con el registro de estrategias
att_inventario = pd.read_csv("/opt/sisepuede/docs/source/csvs/attribute_dim_strategy_id.csv")

if not int(tx_id) in att_inventario.strategy_id.to_list():
   att_inventario = pd.concat([att_inventario,strategy_data_to_csv], ignore_index = True)
   att_inventario.to_csv("/opt/sisepuede/docs/source/csvs/attribute_dim_strategy_id.csv", index = False)
   
   # Agregamos el chunk de código al programa sisepuede/python/define_transformations_integrated.py
   comando = 'sed -i -e "901r /opt/strategy_ssp.txt" /opt/sisepuede/python/define_transformations_integrated.py'
   subprocess.run(comando, shell=True)
   

