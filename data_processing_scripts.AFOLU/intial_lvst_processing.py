# Based on Hermilo's original program to create livestocks input.
# Maintainer: Juan Antonio Robledo


import pandas as pd
import os

# Base directory path for AFOLU
base_path = "../AFOLU"

# Livestock types and their corresponding folders
livestock_types = [
    "pop_lvst_initial_buffalo",
    "pop_lvst_initial_cattle_dairy",
    "pop_lvst_initial_cattle_nondairy",
    "pop_lvst_initial_chickens",
    "pop_lvst_initial_goats",
    "pop_lvst_initial_horses",
    "pop_lvst_initial_mules",
    "pop_lvst_initial_pigs",
    "pop_lvst_initial_sheep",
]

# Path for raw data and FAOSTAT data
data_path = os.path.join(base_path, "pop_lvst_data_raw")
fao_data_file_name = "FAOSTAT_data.csv"
items_classification_file = "items_classification.csv"

# Load FAOSTAT data
encode = "ISO-8859-1"
fao_data = pd.read_csv(os.path.join(data_path, fao_data_file_name), encoding=encode)

# Load country and item classification data
m49_fao_countries = pd.read_json("../AFOLU/pop_lvst_data_raw/m49-countries.json")
cw_fao_names_iso_code3 = {i: j for i, j in zip(m49_fao_countries["country_name_en"], m49_fao_countries["ISO3"])}
fao_data["iso_code3"] = fao_data["Area"].replace(cw_fao_names_iso_code3)
fao_data["iso_code3"] = fao_data["iso_code3"].replace({'TÃ¼rkiye': 'TUR', 'United Kingdom of Great Britain and Northern Ireland': "GBR", "CÃ´te d'Ivoire": "CIV"})  # Manually checked

# Load item classification crosswalk
cw = pd.read_csv(os.path.join(data_path, items_classification_file))[["Item_Fao", "File_Sisepuede"]]
fao_data = fao_data[fao_data.Item.isin(cw.Item_Fao)]
cw_dict = {i: j for i, j in zip(cw["Item_Fao"], cw["File_Sisepuede"])}
fao_data["sisepuede_item"] = fao_data["Item"].replace(cw_dict)

# Group and pivot data
fao_data_grouped = fao_data.groupby(["iso_code3", "Area", "Year", "sisepuede_item"])["Value"].mean().reset_index()
fao_data_pivot = fao_data_grouped.pivot_table(index=['iso_code3', 'Area', 'Year'], columns='sisepuede_item', values='Value').reset_index()
fao_data_pivot = fao_data_pivot.rename(columns={"Area": "Nation"})
fao_data_pivot["pop_lvst_initial_cattle_dairy"] = fao_data_pivot["pop_lvst_initial_cattle_nondairy"].copy()

# Prevent interpolation from affecting rows with value == 0
for livestock_type in livestock_types:
    # Copy relevant data (specific to each livestock type)
    fao_data_livestock = fao_data_pivot.copy()

    # Historical data handling
    path_historical_data = os.path.join(base_path, livestock_type, "input_to_sisepuede", "historical")

    if fao_data_livestock[livestock_type].isna().any():
        # Ensure only non-zero rows are interpolated
        fao_data_livestock[livestock_type] = fao_data_livestock.groupby(["Nation"])[livestock_type].apply(
            lambda x: x if (x == 0).all() else x.interpolate().bfill().fillna(0)).reset_index(drop=True)

    # Save historical data
    historical_file_path = os.path.join(path_historical_data, f"{livestock_type}.csv")
    fao_data_livestock[["iso_code3", "Nation", "Year", livestock_type]].to_csv(historical_file_path, index=False)

    # Projected data handling
    max_year = fao_data_livestock.Year.max()
    fao_data_projected = fao_data_livestock.query(f"Year=={max_year}").drop(columns="Year")

    df_year = pd.DataFrame({"Year": range(max_year + 1, 2051)})
    fao_data_projected = fao_data_projected.merge(df_year, how="cross")

    # Save projected data
    path_projected_data = os.path.join(base_path, livestock_type, "input_to_sisepuede", "projected")
    projected_file_path = os.path.join(path_projected_data, f"{livestock_type}.csv")
    fao_data_projected[["iso_code3", "Nation", "Year", livestock_type]].to_csv(projected_file_path, index=False)

print("Historical and projected data generated for all livestock types.")
