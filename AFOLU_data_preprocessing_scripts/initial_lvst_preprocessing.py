"""
This script allows to update all the initial livestock data (inputs to sisepuede) in the AFOLU directory in a single run.
It uses the raw data stored in AFOLU/pop_lvst_data_raw.

Author: Juan Antonio Robledo
"""

import pandas as pd
import os
from metadata_updater import MetadataUpdater

# Set paths for raw data
raw_data_path = '../AFOLU/pop_lvst_raw_data'
raw_data_file_name = 'FAOSTAT_livestock_data.csv'

# Import raw data csv
lvst_raw_df = pd.read_csv(os.path.join(raw_data_path, raw_data_file_name))

# Drop irrelevant columns
lvst_df = lvst_raw_df[['Area Code (ISO3)', 'Area', 'Year', 'Item', 'Value']]
lvst_df = lvst_df.rename(columns={'Area Code (ISO3)':'iso_code3', 'Area':'Nation'})

# Create a dictionary from items_classification.csv to decide the format and which livestock items we will use to create the inptus for sisepuede
cw_df = pd.read_csv(os.path.join(raw_data_path,'items_classification.csv'))
cw_dict = dict(zip(cw_df['Item_Fao'], cw_df['File_Sisepuede']))

# Filter the data to only get the livestock items in the cw file
lvst_df = lvst_df[lvst_df.Item.isin(cw_df.Item_Fao)]

# Create a new column with the sisepuede item names
lvst_df["sisepuede_item"] = lvst_df["Item"].replace(cw_dict)

# Perform a groupby in case several Items from FAO share the same sisepuede item
# lvst_grouped_df = lvst_df.groupby(["iso_code3", "Nation","Year","sisepuede_item"])["Value"].mean().reset_index()  # The groupby is creating an error in the measurements it is not yet necessary
lvst_pivot_df = lvst_df.pivot_table(index=['iso_code3', 'Nation', 'Year'], columns='sisepuede_item', values='Value').reset_index()  
lvst_pivot_df["pop_lvst_initial_cattle_dairy"] = lvst_pivot_df["pop_lvst_initial_cattle_nondairy"].copy()

# Generate new csv files for each selected livestock item
for sisepuede_var_name in [i for i in lvst_pivot_df.columns if "pop_lvst" in i]:
    
    if lvst_pivot_df[sisepuede_var_name].isna().any():   
        lvst_pivot_df[sisepuede_var_name] = lvst_pivot_df[sisepuede_var_name].fillna(0)

    # Save the new df in its directory.
    dir_path = f'../AFOLU/{sisepuede_var_name}/input_to_sisepuede'    
    lvst_pivot_df[["iso_code3","Nation", "Year",sisepuede_var_name]].to_csv(os.path.join(dir_path,f"historical/{sisepuede_var_name}.csv"), index = False)

# Generate projected input data
max_year = lvst_pivot_df.Year.max()

projected_lvst_df = lvst_pivot_df[lvst_pivot_df.Year == max_year]

projected_lvst_df = projected_lvst_df.drop(columns = "Year")

projected_years_df = pd.DataFrame({"Year" : range(max_year+1, 2051)})
projected_lvst_df = projected_lvst_df.merge(projected_years_df, how = "cross") 


for sise_var in [i for i in lvst_pivot_df.columns if "pop_lvst" in i]:
    dir_path = f'../AFOLU/{sise_var}/input_to_sisepuede'
    projected_lvst_df[["iso_code3","Nation", "Year",sise_var]].to_csv(os.path.join(dir_path,f"projected/{sise_var}.csv"), index = False)

# Update Metadata
variable_info = {
    'name': '',
    'subsector': 'Agriculture',
    'longname': 'Initial Livestock',
    'units': 'number of animals'
}

resource_info = {
    'url': 'https://www.fao.org/faostat/en/#data/QCL',
    'descrip': 'FAOSTAT Crops and livestock products'
}

additional_info = {
    'assumptions': 'The projected values are equal to the last historical value.'
}

for sise_var in [i for i in lvst_pivot_df.columns if "pop_lvst" in i]:

    dir_path = f'../AFOLU/{sise_var}/docs'
    # update the YAML file for each crop item
    variable_info['name'] = sise_var
    updater = MetadataUpdater(os.path.join(dir_path,'metadata.yml'))
    updater.update_yml(variable_info, resource_info, additional_info)


print('Initial livestock data has been updated!')