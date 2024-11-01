import pandas as pd

columnas = [
#"nemomod_entc_frac_min_share_production_pp_biomass",
#"nemomod_entc_frac_min_share_production_pp_coal",
#"nemomod_entc_frac_min_share_production_pp_hydropower",
"nemomod_entc_frac_min_share_production_pp_gas",
"nemomod_entc_frac_min_share_production_pp_nuclear",
"nemomod_entc_frac_min_share_production_pp_oil",
#"nemomod_entc_frac_min_share_production_pp_solar",
#"nemomod_entc_frac_min_share_production_pp_wind",
#"nemomod_entc_frac_min_share_production_pp_geothermal",
#"nemomod_entc_frac_min_share_production_pp_ocean"
]

tony = pd.read_csv("new_iran_pp_data.csv")
df = pd.read_csv("real_data_antes_energia/real_data.csv")

df[columnas] = tony[columnas]

df.to_csv("real_data.csv", index = False)


