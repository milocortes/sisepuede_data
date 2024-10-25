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



def get_strategies_from_codes(
    strategy_codes: Union[List[str], str],
) -> Union[List[int], None]:
    """
    Map codes to id as input
    """
    attr_strat = sa.model_attributes.get_dimensional_attribute_table(sa.model_attributes.dim_strategy_id)
    dict_map = attr_strat.field_maps.get(f"strategy_code_to_{attr_strat.key}")
 
    # check specification of codes
    strategy_codes = (
        [strategy_codes]
        if isinstance(strategy_codes, str)
        else (
            strategy_codes
            if sf.islistlike(strategy_codes)
            else None
        )
    )
 
    if strategy_codes is None:
        return None
 
    # get ids to build
    strategies_build = [dict_map.get(x) for x in strategy_codes]
    strategies_build = [x for x in strategies_build if x is not None]
    out = (
        None
        if len(strategies_build) == 0
        else strategies_build
    )
 
    return out
 
strategy_codes_keep = [
    "BASE",
    "PFLO:ALL_PLUR",
    "PFLO:CHANGE_CONSUMPTION",
    "PFLO:BETTER_BASE",
    "LNDU:PLUR"]
 
strategies_keep = get_strategies_from_codes(strategy_codes_keep)
 
transformations_integrated.build_strategies_to_templates(strategies = [1015, 1014, 5001, 4008, 5004, 5004, 5005, 5006, 5007, 5008, 5009])


