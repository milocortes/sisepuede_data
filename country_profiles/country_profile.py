##
import pandas as pd
import os
import yaml

class CountryProfile:

    def __init__(self) -> None:
        pass

    
    def get_country_profile_data(self, category_dir_path, iso_code3, type_of_input='historical'):
        # List all directories in the specified directory
        indicator_dir_list = [d for d in os.listdir(category_dir_path) if os.path.isdir(os.path.join(category_dir_path, d))]
        indicator_dir_list.sort()
        
        # Initialize an empty DataFrame for merging historical data
        merged_df = pd.DataFrame()

        # Loop in every input folder to look for historical data CSV
        for indicator_dir in indicator_dir_list:
            input_dir_path = os.path.join(category_dir_path, indicator_dir, 'input_to_sisepuede')
            historical_file_path = os.path.join(input_dir_path, f'{type_of_input}/{indicator_dir}.csv')
            
            if os.path.isfile(historical_file_path):
                # Open the historical DataFrame
                hist_df = pd.read_csv(historical_file_path)
                
                # Filter by the country we want
                try:
                    country_only_df = hist_df[hist_df.iso_code3 == iso_code3].reset_index(drop=True)
                
                except KeyError:
                    print(f'{indicator_dir} has no iso_code3 col')
                    continue
                    
                # Check if the 'Year' column exists in the current DataFrame
                if 'Year' not in country_only_df.columns:
                    print(f'{indicator_dir} does not have a Year column')
                    continue

                # Making sure Nation col is dropped
                country_only_df = country_only_df[['Year', 'iso_code3', indicator_dir]]

                # Merge with the master DataFrame (outer join on 'Year' and 'iso_code3')
                if merged_df.empty:
                    merged_df = country_only_df  # Initialize with the first DataFrame
                else:
                    merged_df = pd.merge(merged_df, country_only_df, on=['Year', 'iso_code3'], how='outer')

            else:
                print(f'{indicator_dir} does not have an sisepuede_input CSV file, skipping...')
                continue
        
        # After looping through all the historical files, return or print the merged DataFrame
        if not merged_df.empty:
            return merged_df
        else:
            print("No data found for the specified country.")
        
    def create_csv_files(self, country_name, iso_code3):
        # Read config yaml file to obtain sisepuede categories
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

        # Access the list of categories
        categories = config['sisepuede_categories']

        for category in categories:

            category_dir_path = f'../{category}'
            
            for type_of_input in ['historical', 'projected']: 
                category_df = self.get_country_profile_data(category_dir_path, iso_code3, type_of_input)
                save_path = os.path.join(country_name, f'{category}_{type_of_input}.csv')
                category_df.to_csv(save_path, index=False)
                print(f'{type_of_input} CSV file created for {category}')
            


    def create_country_profile(self, country_name, iso_code3):

        # Create the country profile directory
        os.makedirs(country_name, exist_ok=True)

        # Create the csv files for each sisepuede category
        self.create_csv_files(country_name, iso_code3)