# Carga bibliotecas
import pandas as pd
import sys
import os

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

from typing import List

# Carga csvs directo del repositorio de Costos y Beneficios
NIDHI_REPO_DATA_PATH = '/opt/sisepuede_costs_benefits/strategy_specific_cb_files'

# Agriculture and Livestock Productivity
agrc_lvst_productivity = pd.read_csv(os.path.join(NIDHI_REPO_DATA_PATH, 'AGRC_LVST_productivity_cost_gdp.csv'))

# Land Use Soil Carbon Fractions
lndu_soil_carbon_fractions = pd.read_csv(os.path.join(NIDHI_REPO_DATA_PATH, 'LNDU_soil_carbon_fractions.csv'))

# Entc reduce losses Cost
entc_reduce_losses_cost_file = pd.read_excel(os.path.join(NIDHI_REPO_DATA_PATH, 'ENTC_REDUCE_LOSSES_cost_file.xlsx') , sheet_name = 'Annual Loss Reduction Cost')

# Cargamos la ruta del sisepuede para hacer uso de algunas utilerías
SSP_PYTHON_PATH = '/opt/sisepuede/python'
sys.path.append(SSP_PYTHON_PATH)

# Cargamos el paquete setup_analysis de sisepuede, el cual contiene metadatos del modelo
import setup_analysis as sa
import support_classes as sc    
import sisepuede_file_structure as sfs

file_struct = sfs.SISEPUEDEFileStructure()
model_attributes = file_struct.model_attributes
regions = sc.Regions(model_attributes)

regions_table = regions.attributes.table.copy()

# Usaremos K-means usando las características de PIB per cápita y área del país.
def build_path_ssp_data(ssp_socio_eco : str) -> str:
    return f'https://raw.githubusercontent.com/milocortes/sisepuede_data/main/SocioEconomic/{ssp_socio_eco}/input_to_sisepuede/historical/{ssp_socio_eco}.csv'

ssp_socioec = {
    'gdp' : 'gdp_mmm_usd',
    'urban_pop' : 'population_gnrl_urban',
    'rural_pop' : 'population_gnrl_rural',
    'area' : 'area_gnrl_country_ha'
}

regions_features = pd.DataFrame()

for k,v in ssp_socioec.items():
    df_socioec = pd.read_csv(build_path_ssp_data(v))
    regions_features = pd.concat([regions_features, df_socioec.set_index(['Nation', 'iso_code3', 'Year'])], axis = 1)

regions_features = regions_features.reset_index()

## Nos quedamos sólo con las regiones de SSP para el año 2015
regions_features = regions_features[regions_features.iso_code3.isin(regions_table.iso_alpha_3)].query('Year==2010 and gdp_mmm_usd>0.0 and area_gnrl_country_ha>0.0')
regions_features = regions_features[['iso_code3', 'gdp_mmm_usd', 'area_gnrl_country_ha']]

## Pobramos Kmedias con varios cluster y usamos la métrica de silueta para decidir la cantidad que minimiza la métrica
regions_features['gdp_mmm_usd_log'] = np.log(regions_features.gdp_mmm_usd)
regions_features['area_gnrl_country_ha_log'] = np.log(regions_features.area_gnrl_country_ha)

X = regions_features[['gdp_mmm_usd_log', 'area_gnrl_country_ha_log']].to_numpy()

for k_num in range(2,8):

    kmeans = KMeans(n_clusters=k_num, random_state=0, n_init='auto').fit(X)
    silueta = silhouette_score(X, kmeans.fit_predict(X))
    print(f'K num : {k_num}. Silueta : {silueta}')

## The best value is 1 and the worst value is -1. Values near 0 indicate overlapping clusters. Negative values generally indicate that a sample has been assigned to the wrong cluster, as a different cluster is more similar.
## Usaremos 7 cluster, a pesar que el mejor valor se da con 2 cluster

kmeans = KMeans(n_clusters=7, random_state=0, n_init='auto').fit(X)
regions_features['label'] = kmeans.labels_

## Crearemos un diccionario para identificar los paises de LAC de acuerdo al grupo que les asignó el algoritmo
LAC_regions = regions_features[regions_features.iso_code3.isin(lndu_soil_carbon_fractions.ISO3)]
LAC_k_means = {i: [] for i in LAC_regions.label}
ISO_LAC_LABEL_k_means = {}

for label, ISO in LAC_regions[['label', 'iso_code3']].to_records(index = False):
    LAC_k_means[label].append(ISO)
    ISO_LAC_LABEL_k_means[ISO] = label

## Agrupamos los datos de Agriculture and Livestock Productivity, Land Use Soil Carbon Fractions y Entc reduce losses Cost

# Agriculture and Livestock Productivity
agrc_lvst_productivity_label = agrc_lvst_productivity[agrc_lvst_productivity.iso_code3.isin(ISO_LAC_LABEL_k_means.keys()) ].copy()
agrc_lvst_productivity_label['label'] = agrc_lvst_productivity_label.iso_code3.replace(ISO_LAC_LABEL_k_means)
agrc_lvst_productivity_label = agrc_lvst_productivity_label[['label', 'cost_of_productivity improvements_pct_gdp', 'cost_of_productivity improvements_pct_gdp_orig']].groupby('label').mean().reset_index()

# Land Use Soil Carbon Fractions
lndu_soil_carbon_fractions_label = lndu_soil_carbon_fractions[lndu_soil_carbon_fractions.ISO3.isin(ISO_LAC_LABEL_k_means.keys()) ].copy()
lndu_soil_carbon_fractions_label['label'] = lndu_soil_carbon_fractions_label.ISO3.replace(ISO_LAC_LABEL_k_means)
lndu_soil_carbon_fractions_label = lndu_soil_carbon_fractions_label[['label', 'start_val', 'end_val']].groupby('label').mean().reset_index()

# Entc reduce losses Cost
entc_reduce_losses_cost_file_label = entc_reduce_losses_cost_file[entc_reduce_losses_cost_file.ISO3.isin(ISO_LAC_LABEL_k_means.keys()) ].copy()
entc_reduce_losses_cost_file_label['label'] = entc_reduce_losses_cost_file_label.ISO3.replace(ISO_LAC_LABEL_k_means)
entc_reduce_losses_cost_file_label = entc_reduce_losses_cost_file_label[['label', 'annual_investment_USD']].groupby('label').mean().reset_index()

# Agregamos las variables al data frame regions_features, excluyendo los paises de LAC
lac_all_countries = agrc_lvst_productivity.iso_code3.to_list()
regions_features = regions_features[~regions_features.iso_code3.isin(lac_all_countries)]
regions_features = regions_features.merge(right=agrc_lvst_productivity_label, how = 'left', on = 'label').\
                merge(right=lndu_soil_carbon_fractions_label, how = 'left', on = 'label').\
                merge(right=entc_reduce_losses_cost_file_label, how = 'left', on = 'label')


regions_features['region'] = regions_features['iso_code3'].replace( {i:j for i,j in regions_table[['iso_alpha_3', 'region']].to_records(index = False)})
regions_features['category_name'] = regions_features['iso_code3'].replace( {i:j for i,j in regions_table[['iso_alpha_3', 'category_name']].to_records(index = False)})

# Agregamos adicional a los dataframes originales
agrc_lvst_productivity_complete = pd.concat([agrc_lvst_productivity,regions_features[['iso_code3', 'cost_of_productivity improvements_pct_gdp', 'cost_of_productivity improvements_pct_gdp_orig']]], ignore_index = True)
lndu_soil_carbon_fractions_complete = pd.concat([lndu_soil_carbon_fractions[['region', 'ISO3', 'start_val', 'end_val']] ,
                            regions_features[['region', 'iso_code3', 'start_val', 'end_val']].rename(columns = {'iso_code3':'ISO3'})], ignore_index = True)

entc_reduce_losses_cost_file_complete = pd.concat([entc_reduce_losses_cost_file[['Country ', 'ISO3', 'annual_investment_USD']] ,
                            regions_features[['category_name', 'iso_code3', 'annual_investment_USD']].rename(columns = {'category_name' : 'Country ', 'iso_code3':'ISO3'})], ignore_index = True)


## Reescribimos los archivos
# Agriculture and Livestock Productivity
agrc_lvst_productivity_complete.to_csv(os.path.join(NIDHI_REPO_DATA_PATH, 'AGRC_LVST_productivity_cost_gdp.csv'), index = False)

# Land Use Soil Carbon Fractions
lndu_soil_carbon_fractions_complete.to_csv(os.path.join(NIDHI_REPO_DATA_PATH, 'LNDU_soil_carbon_fractions.csv'), index = False)

# Entc reduce losses Cost
writer = pd.ExcelWriter(os.path.join(NIDHI_REPO_DATA_PATH, 'ENTC_REDUCE_LOSSES_cost_file.xlsx'))
entc_reduce_losses_cost_file_complete.to_excel(writer, sheet_name = 'Annual Loss Reduction Cost', index = False)
writer.close()