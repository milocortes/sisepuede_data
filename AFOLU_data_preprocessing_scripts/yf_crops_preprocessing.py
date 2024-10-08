"""
This script allows to update all the crop yield factor data (inputs to sisepuede) in the AFOLU directory in a single run.
It uses the raw data stored in AFOLU/yf_agrc_raw_data.

Author: Juan Antonio Robledo
"""

import pandas as pd
import os
from metadata_updater import MetadataUpdater

# Set raw files path
raw_data_path = '../AFOLU/yf_agrc_raw_data'
raw_data_file_name = 'FAOSTAT_crop_data.csv'

# Import raw data from FAO csv file
raw_data_df = pd.read_csv(os.path.join(raw_data_path, raw_data_file_name))

# Drop irrelevant columns and modify names to match SISEPUEDE input style
yf_df = raw_data_df[['Area Code (ISO3)', 'Area', 'Item', 'Year', 'Value']]
yf_df = yf_df.rename(columns={'Area Code (ISO3)':'iso_code3', 'Area':'Nation'})

# Importing crosswalk file
cw_df = pd.read_csv("https://raw.githubusercontent.com/jcsyme/sisepuede/main/ref/data_crosswalks/fao_crop_categories.csv")
cw_df = cw_df.rename(columns = {"fao_crop" : "Item", "``$CAT-AGRICULTURE$``" : "sisepuede_item"})
cw_df["sisepuede_item"] = cw_df["sisepuede_item"].apply(lambda x : f"yf_agrc_{x}_tonne_ha")

# Creating crosswalk dictionary
cw_dict = dict(zip(cw_df['Item'], cw_df['sisepuede_item']))

# Adding a column with sisepuede_items input style using the cw dictionary
yf_df["sisepuede_item"] = yf_df["Item"].replace(cw_dict)
yf_df = yf_df.query("Item != 'Maté'") # Queries all data except where item == Mate

# Performing groupby since many items from FAO where mapped to the same category
yf_df_grouped = yf_df.groupby(["iso_code3", "Nation","Year","sisepuede_item"])["Value"].mean().reset_index()

# Pivot dataframe so its easier to handle it
yf_df_pivot = yf_df_grouped.pivot(index=['iso_code3', 'Nation', 'Year'], columns='sisepuede_item', values='Value').reset_index()

# Create historical input data
sisepuede_items = yf_df_grouped.sisepuede_item.unique()

for sise_var in sisepuede_items:

    # Convertion Kilograms to Ton (metric) : 1 kg = 0.00110231 t
    yf_df_pivot[sise_var] *= 0.00110231 # Change this value if the raw data is in different units

    if yf_df_pivot[sise_var].isna().any():

        yf_df_pivot[sise_var] = yf_df_pivot.groupby(["Nation"])[sise_var].apply(lambda x: x.interpolate().fillna(method='bfill')).reset_index()[sise_var].fillna(0)
    
    dir_path = f'../AFOLU/{sise_var}/input_to_sisepuede'
    yf_df_pivot[["iso_code3","Nation", "Year", sise_var]].to_csv(os.path.join(dir_path,f"historical/{sise_var}.csv"), index = False)



# Create projected input data
max_year = yf_df_pivot.Year.max()

yf_data_projected = yf_df_pivot.query(f"Year=={max_year}")

yf_data_projected = yf_data_projected.drop(columns = "Year")

df_year = pd.DataFrame({"Year" : range(max_year+1, 2051)})

yf_data_projected = yf_data_projected.merge(df_year, how = "cross") 

for sise_var in sisepuede_items:
    dir_path = f'../AFOLU/{sise_var}/input_to_sisepuede'
    yf_data_projected[["iso_code3","Nation", "Year",sise_var]].to_csv(os.path.join(dir_path,f"projected/{sise_var}.csv"), index = False)


# Update Metadata
variable_info = {
    'name': '',
    'subsector': 'Agriculture',
    'longname': 'Crop Yield Factor',
    'units': 'Tonnes per Hectare'
}

resource_info = {
    'url': 'https://www.fao.org/faostat/en/#data/QCL',
    'descrip': 'FAOSTAT Crops and livestock products'
}

additional_info = {
    'assumptions': 'The projected values are equal to the last historical value.'
}

for sise_var in sisepuede_items:

    dir_path = f'../AFOLU/{sise_var}/docs'
    # update the YAML file for each crop item
    variable_info['name'] = sise_var
    updater = MetadataUpdater(os.path.join(dir_path,'metadata.yml'))
    updater.update_yml(variable_info, resource_info, additional_info)


print('Crop yield factor data has been updated!')