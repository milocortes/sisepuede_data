"""
This script allows to update all the initial livestock data (inputs to sisepuede) in the AFOLU directory in a single run.
It uses the raw data stored in AFOLU/pop_lvst_data_raw.

Author: Juan Antonio Robledo
"""

import pandas as pd
import os

# function to handle special cases
def handle_special_cases(row):
    if row['Nation'] == 'China, mainland' or row['Nation'] == 'China, Taiwan Province of' or row['Nation'] == 'Sudan (former)':
        return row['Nation']  # Copy the Nation name to the iso_code3 column
    elif row['Nation'] == 'Netherlands (Kingdom of the)':
        row['Nation'] = 'Netherlands'  # Change Nation name to 'Netherlands'
        return 'NLD'  # Set iso_code3 to 'NLD'
    elif row['Nation'] == 'United Kingdom of Great Britain and Northern Ireland':
        return 'GBR'  # Set iso_code3 to 'GBR'
    elif row['Nation'] == 'Türkiye':
        return 'TUR'  # Set iso_code3 to 'TUR'
    else:
        return row['iso_code3']  # Return the existing ISO3 code if no special case

raw_data_path = '../AFOLU/pop_lvst_data_raw'
lvst_df = pd.read_csv(os.path.join(raw_data_path, 'FAOSTAT_data.csv'))

# Drop irrelevant columns
lvst_relevant_df = lvst_df[['Area', 'Year', 'Item', 'Value']]
lvst_relevant_df = lvst_relevant_df.rename(columns={'Area':'Nation'})

# Load m49 JSON to get ISO3 country codes.
df_json = pd.read_json(os.path.join(raw_data_path, 'm49-countries.json'))

# Create a new column with the ISO3 country codes
lvst_merged_df = lvst_relevant_df.merge(df_json, how='left', left_on='Nation', right_on='country_name_en')
lvst_merged_df = lvst_merged_df[['ISO3', 'Nation', 'Year', 'Item', 'Value']]
lvst_merged_df = lvst_merged_df.rename(columns={'ISO3': 'iso_code3'})

# Apply the function to deal with ISO3 special cases to the rows
lvst_merged_df['iso_code3'] = lvst_merged_df.apply(handle_special_cases, axis=1)

# Create a dictionary from items_classification.csv to decide the format and which livestock items we will use to create the inptus for sisepuede
crosswalk_df = pd.read_csv(os.path.join(raw_data_path,'items_classification.csv'))
crosswalk_df_dict = dict(zip(crosswalk_df['Item_Fao'], crosswalk_df['File_Sisepuede']))

# Generate new csv files for each selected livestock item
for lvst_item in crosswalk_df_dict.keys():
    
    # Generate historical input data
    historical_lvst_df = lvst_merged_df[lvst_merged_df.Item == lvst_item]
    sisepuede_input_name = crosswalk_df_dict[lvst_item]

    # Apply bfill and ffill within each country group (grouped by 'iso_code3') only if there are null values
    if historical_lvst_df['Value'].isnull().any():
        historical_lvst_df['Value'] = historical_lvst_df.groupby('iso_code3')['Value'].apply(lambda group: group.bfill().ffill())
    
    # Rename and drop columns to match SISEPUEDE format
    historical_lvst_df = historical_lvst_df.drop(columns=['Item'])
    historical_lvst_df = historical_lvst_df.rename(columns={'Value': sisepuede_input_name})

    # Save the new df in its directory.
    dir_path = f'../AFOLU/{sisepuede_input_name}/input_to_sisepuede'
    historical_lvst_df.to_csv(os.path.join(dir_path, f'historical/{sisepuede_input_name}.csv'), index = False)
    
    # Generate projected input data
    max_year = historical_lvst_df.Year.max()

    projected_lvst_df = historical_lvst_df[historical_lvst_df.Year == max_year]

    projected_lvst_df = projected_lvst_df.drop(columns = "Year")

    projected_years_df = pd.DataFrame({"Year" : range(max_year+1, 2051)})
    projected_lvst_df = projected_lvst_df.merge(projected_years_df, how = "cross") 

    projected_lvst_df.to_csv(os.path.join(dir_path, f"projected/{sisepuede_input_name}.csv"), index = False)

    # Generate file for cattle non-dairy
    if lvst_item == 'Cattle':
        """
        Cattle,pop_lvst_initial_cattle_nondairy,I assume 50% of cattle in FAO is nondairy

        This just copies the cattle dairy to non-dairy. Perhaps we need to change this to something else
        """
        historical_lvst_df.to_csv(os.path.join(dir_path, f'historical/pop_lvst_initial_cattle_nondairy.csv'), index = False)
        projected_lvst_df.to_csv(os.path.join(dir_path, f"projected/pop_lvst_initial_cattle_nondairy.csv"), index = False)

print('Initial livestock data has been updated!')