import pandas as pd 

### CW INDIA:SSP
cw_india_ssp = {
    'croplands' : ('Crop',),
    #'forests_mangroves' : (None), # manglares
    'forests_primary' : ('Med/dense forest',),
    'forests_secondary' : ('Open forest',),
    'grasslands' : ('Grassland',),
    'other' : ('Plantation_agrofor', 'Shrub', 'Wasteland', 'Fallowland', 'Water_ice'),
    'settlements' : ('Urban_built', 'Total Urban'),
    'wetlands' : ('Swamp_rann',)
}


# Total area 2070 [million HA]
total_area_2070 = {
    "Med/dense forest" : 87.6016,
    "Crop" : 139.1817,
    "Grassland" : 1.9343,
    "Plantation_agrofor" : 37.1607,
    "Shrub" : 10.2004,
    "Wasteland" : 0.424,
    "Fallowland" : 1.5948,
    "Swamp_rann" : 1.9598,
    "Water_ice" : 13.6304,
    "Urban_built" : 9.7851,
    "Open forest" : 0.9359,
    "Total Urban" : 16.37164382
}

df_total_area_2070 = pd.DataFrame([(i,j) for i,j in total_area_2070.items()], columns = ["lndu_india", "million_ha"])
 
# Total area 2019 [million HA]
total_area_2019 = {
    "Med/dense forest" : 37.1493,
    "Crop" : 139.7819,
    "Grassland"	: 1.9838,
    "Plantation_agrofor" : 9.505,
    "Shrub" : 10.8059,
    "Wasteland" : 31.8382,
    "Fallowland" : 29.598,
    "Swamp_rann" : 1.9604,
    "Water_ice" : 16.7391,
    "Urban_built" : 9.9423,
    "Open forest" : 25.926,
    "Total Urban" : 5.550443825,
}

df_total_area_2019 = pd.DataFrame([(i,j) for i,j in total_area_2019.items()], columns = ["lndu_india", "million_ha"])

### Valores en SSP
ssp_total_area_2019 = {k: df_total_area_2019[df_total_area_2019["lndu_india"].isin(v)].million_ha.sum()  for k,v in cw_india_ssp.items()}
ssp_total_area_2070 = {k: df_total_area_2070[df_total_area_2070["lndu_india"].isin(v)].million_ha.sum()  for k,v in cw_india_ssp.items()}

ssp_shares_area_2019 = {i : j/sum(ssp_total_area_2019.values()) for i,j in ssp_total_area_2019.items() }
ssp_shares_area_2070 = {i : j/sum(ssp_total_area_2070.values()) for i,j in ssp_total_area_2070.items() }
