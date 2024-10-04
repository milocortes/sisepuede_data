import pandas as pd
import os
import sys

# Argument for the variable name in the sisepuede system
sisepuede_var_name = sys.argv[1]

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
fao_data_file_name = "FAOSTAT_data_en_10-4-2024.csv"
items_classification_file = "items_classification.csv"

# Load FAOSTAT data
encode = "ISO-8859-1"
fao_data = pd.read_csv(os.path.join(data_path, fao_data_file_name), encoding=encode)

# Load country and item classification data
m49_fao_countries = pd.read_json("https://data.apps.fao.org/catalog/dataset/1712bf04-a530-4d55-bb66-54949213985f/resource/b0c1d224-23ea-425d-b994-e15f76feb26b/download/m49-countries.json")
cw_fao_names_iso_code3 = {i: j for i, j in zip(m49_fao_countries["country_name_en"], m49_fao_countries["ISO3"])}
fao_data["iso_code3"] = fao_data["Area"].replace(cw_fao_names_iso_code3)
fao_data["iso_code3"] = fao_data["iso_code3"].replace({'T?rkiye': 'TUR', 'United Kingdom of Great Britain and Northern Ireland': "GBR", "C?te d'Ivoire": "CIV"})

# Load item classification crosswalk
cw = pd.read_csv(os.path.join(data_path, items_classification_file))[["Item_Fao", "File_Sisepuede"]]
fao_data = fao_data[fao_data.Item.isin(cw.Item_Fao)]
cw_dict = {i: j for i, j in zip(cw["Item_Fao"], cw["File_Sisepuede"])}
fao_data["sisepuede_item"] = fao_data["Item"].replace(cw_dict)

# Group and pivot data
fao_data_grouped = fao_data.groupby(["iso_code3", "Area", "Year", "sisepuede_item"])["Value"].mean().reset_index()
fao_data_pivot = fao_data_grouped.pivot_table(index=['iso_code3', 'Area', 'Year'], columns='sisepuede_item', values='Value').reset_index()
fao_data_pivot = fao_data_pivot.rename(columns={"Area": "Nation"})

# Loop through each livestock type folder
for livestock_type in livestock_types:
    # Copy relevant data (specific to each livestock type)
    fao_data_livestock = fao_data_pivot.copy()
    fao_data_livestock["pop_lvst_initial_cattle_dairy"] = fao_data_pivot["pop_lvst_initial_cattle_nondairy"].copy()

    # Historical data handling
    path_historical_data = os.path.join(base_path, livestock_type, "input_to_sisepuede", "historical")

    if fao_data_livestock[sisepuede_var_name].isna().any():
        fao_data_livestock[sisepuede_var_name] = fao_data_livestock.groupby(["Nation"])[sisepuede_var_name].apply(
            lambda x: x.interpolate().fillna(method='bfill')).reset_index()[sisepuede_var_name].fillna(0)

    # Save historical data
    historical_file_path = os.path.join(path_historical_data, f"{sisepuede_var_name}.csv")
    fao_data_livestock[["iso_code3", "Nation", "Year", sisepuede_var_name]].to_csv(historical_file_path, index=False)

    # Projected data handling
    max_year = fao_data_livestock.Year.max()
    fao_data_projected = fao_data_livestock.query(f"Year=={max_year}").drop(columns="Year")

    df_year = pd.DataFrame({"Year": range(max_year + 1, 2051)})
    fao_data_projected = fao_data_projected.merge(df_year, how="cross")

    # Save projected data
    path_projected_data = os.path.join(base_path, livestock_type, "input_to_sisepuede", "projected")
    projected_file_path = os.path.join(path_projected_data, f"{sisepuede_var_name}.csv")
    fao_data_projected[["iso_code3", "Nation", "Year", sisepuede_var_name]].to_csv(projected_file_path, index=False)

print("Historical and projected data generated for all livestock types.")
