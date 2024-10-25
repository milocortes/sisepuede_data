import pandas as pd 

df = pd.read_csv("real_data.csv")
turquia = pd.read_csv("real_data_brazil.csv")
fuel_mix = pd.read_csv("frac_trns_fuelmix_updated.csv")
mtkm_dem_freight = pd.read_csv("frac_trns_mtkm_dem_freight.csv")

trns_nan = ['frac_trns_mtkm_dem_freight_road_heavy_freight',
       'frac_trns_fuelmix_road_heavy_regional_hydrogen',
       'frac_trns_mtkm_dem_freight_water_borne',
       'frac_trns_fuelmix_road_heavy_freight_hydrogen',
       'frac_trns_fuelmix_road_heavy_freight_diesel',
       'frac_trns_fuelmix_road_light_gasoline',
       'frac_trns_fuelmix_road_heavy_regional_electricity',
       'frac_trns_fuelmix_public_natural_gas',
       'frac_trns_fuelmix_road_light_hydrogen',
       'frac_trns_fuelmix_road_light_biofuels',
       'frac_trns_fuelmix_road_heavy_freight_electricity',
       'frac_trns_fuelmix_road_heavy_regional_biofuels',
       'frac_trns_mtkm_dem_freight_aviation',
       'frac_trns_fuelmix_public_electricity',
       'frac_trns_fuelmix_public_gasoline',
       'frac_trns_mtkm_dem_freight_rail_freight',
       'frac_trns_fuelmix_public_biofuels',
       'frac_trns_fuelmix_road_heavy_regional_natural_gas',
       'frac_trns_fuelmix_road_heavy_freight_biofuels',
       'frac_trns_fuelmix_road_light_diesel',
       'frac_trns_fuelmix_road_heavy_regional_diesel',
       'frac_trns_fuelmix_road_heavy_freight_gasoline',
       'frac_trns_fuelmix_public_diesel',
       'frac_trns_fuelmix_road_heavy_regional_gasoline',
       'frac_trns_fuelmix_road_light_electricity',
       'frac_trns_fuelmix_road_heavy_freight_natural_gas',
       'frac_trns_fuelmix_public_hydrogen']


#df[[i for i in df.columns if "trns" in i] + ["deminit_trde_freight_mt_km"]] = turquia[[i for i in df.columns if "trns" in i]+ ["deminit_trde_freight_mt_km"]]
df[ ["deminit_trde_freight_mt_km"] + trns_nan] = turquia[["deminit_trde_freight_mt_km"]  + trns_nan]

# Carga fake data complete
fake_data = pd.read_csv("https://raw.githubusercontent.com/jcsyme/sisepuede/refs/heads/main/sisepuede/ref/fake_data/fake_data_complete.csv")

freights = ['frac_trns_mtkm_dem_freight_road_heavy_freight','frac_trns_mtkm_dem_freight_rail_freight','frac_trns_mtkm_dem_freight_aviation', 'frac_trns_mtkm_dem_freight_water_borne']

df[freights] = turquia[freights]
#df[freights] = [0.1, 0.85,0.0, 0.05]
df[fuel_mix.columns[3:]] = fuel_mix[fuel_mix.columns[3:]]


### Variables associated with the Transportation Demand subsector are shown below.
trns_demand = ["deminit_trde_freight_mt_km", "deminit_trde_private_and_public_per_capita_passenger_km", "deminit_trde_regional_per_capita_passenger_km", "elasticity_trde_pkm_to_gdppc_private_and_public", "elasticity_trde_pkm_to_gdppc_regional"]

#df[trns_demand] = turquia[trns_demand]

df[trns_demand] = fake_data[trns_demand]

df["deminit_trde_freight_mt_km"] = fake_data["deminit_trde_freight_mt_km"]*6

#df[mtkm_dem_freight.columns[2:]] = mtkm_dem_freight[mtkm_dem_freight.columns[2:]]
#brazil = pd.read_csv("real_data_brazil.csv")

#df[mtkm_dem_freight.columns[2:]] = brazil[mtkm_dem_freight.columns[2:]]

df.to_csv("real_data.csv", index = False)

