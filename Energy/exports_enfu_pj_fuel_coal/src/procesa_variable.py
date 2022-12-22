import pandas as pd
import os 

# Get Coal export data
variable_to_process = "Coal and coal products"
sisepuede_name = "exports_enfu_pj_fuel_coal"

print(f"Processing {sisepuede_name} variable")

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))

relative_path = os.path.normpath(dir_path + "/../../../")
relative_path_wbal_file = os.path.join(relative_path, "wbal.csv")

# Read source data
wbal = pd.read_csv(relative_path_wbal_file)

wbal_var_to_proc = wbal[['COUNTRY','FLOW','TIME','UNIT',variable_to_process]]
wbal_var_to_proc = wbal_var_to_proc.query("FLOW == 'Exports'")

# Get countries ISO 3 codes
relative_path_iso3_file = os.path.join(relative_path, "iso3_all_countries.csv")
iso3_countries = pd.read_csv(relative_path_iso3_file)

wbal_var_to_proc = wbal_var_to_proc[wbal_var_to_proc["COUNTRY"].isin(iso3_countries["Category Name"])]
wbal_var_to_proc = wbal_var_to_proc.query("COUNTRY !='World'")

wbal_var_to_proc[variable_to_process] = -1*wbal_var_to_proc[variable_to_process].apply(lambda x: float(str(x).replace("..","0")))

# Build variable
asumptions_exports_factors = {
    "Coal and coal products" : 0.22, # Assumption export 0.22 of export coal go to electricity production
    "Electricity" : 1, # Assumption export 1 of export Electricity go to Electricity production
    "Natural gas" : 0.39 # Assumption export 0.39 of export Natural Gas go to electricity production
}

# SOURCE
# https://www.eia.gov/tools/faqs/faq.php?id=427&t=3

factor = asumptions_exports_factors[variable_to_process]
wbal_var_to_proc[variable_to_process]  = wbal_var_to_proc[variable_to_process] * factor

# Convert to TeraJoul to PetaJoul
wbal_var_to_proc = wbal_var_to_proc.query("UNIT=='TJ'")
wbal_var_to_proc[variable_to_process]  = wbal_var_to_proc[variable_to_process]*0.001

# Merge with  ISO 3 codes
wbal_var_to_proc_merge = wbal_var_to_proc.rename(columns = {"COUNTRY":"Category Name"})\
         .merge(right = iso3_countries, how = "left", on = "Category Name")

wbal_var_to_proc_merge = wbal_var_to_proc_merge[["REGION", "ISO3", "TIME", variable_to_process]]

wbal_var_to_proc_merge = wbal_var_to_proc_merge.rename(columns = {"REGION" : "Nation",
                                          "TIME" : "Year",
                                          "ISO3" : "iso_code3",
                                          variable_to_process: sisepuede_name})

# Get countries without values
latam_countries = set(iso3_countries["REGION"][:26])
non_values = latam_countries.symmetric_difference(latam_countries.intersection(wbal_var_to_proc_merge["Nation"]))
 
# Impute values with the Costa Rica values
save_df = []
impute_country_base = wbal_var_to_proc_merge.query(f"Nation == 'costa_rica'").reset_index(drop = True)

for country in non_values:
    impute_country = impute_country_base.copy()
    impute_country["Nation"]= country
    ISO3 , Code = iso3_countries.loc[iso3_countries["REGION"]==country, ["ISO3","Code"]].values[0]
    impute_country["ISO3"]= ISO3
    impute_country["Code"]= Code
    impute_country["sisepuede_name"] = 0 

    save_df.append(impute_country)


wbal_var_to_proc_all = pd.concat([wbal_var_to_proc_merge]+save_df, ignore_index = True)
wbal_var_to_proc_all.sort_values(["Nation","Year"], inplace = True)

## Save historical data

wbal_var_to_proc_all.rename(columns = {"ISO3":"iso_code3"}, inplace = True)

relative_path_to_save_historical = os.path.normpath(dir_path + "/../input_to_sisepuede/historical")

relative_path_to_save_historical_file = os.path.join(relative_path_to_save_historical, f"{sisepuede_name}.csv")

wbal_var_to_proc_all[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_historical_file, index = False)

## Get the last one historical year
last_one_year = max(wbal_var_to_proc_all["Year"])
loy_wbal_var_to_proc_all = wbal_var_to_proc_all.query(f"Year=={last_one_year}").reset_index(drop=True)

## Project with the last value to 2050

acumula_df = []

for i in range(last_one_year, 2050):
    last_one_year += 1
    new_loy_df = loy_wbal_var_to_proc_all.copy()
    new_loy_df["Year"] = last_one_year
    acumula_df.append(new_loy_df)

df_project = pd.concat(acumula_df, ignore_index = True)
df_project.sort_values(["Nation","Year"], inplace = True)

## Save projected data

relative_path_to_save_projected = os.path.normpath(dir_path + "/../input_to_sisepuede/projected")

relative_path_to_save_projected_file = os.path.join(relative_path_to_save_projected, f"{sisepuede_name}.csv")

df_project[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_projected_file, index = False)
