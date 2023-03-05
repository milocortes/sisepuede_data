import pandas as pd
import os 
import sys 

from correspondencias_WEB_sisepuede_revised_jsyme import correspondencias_web_sisepuede

# Get Coal and coal products import data
sisepuede_name = sys.argv[1]
variable_to_process, factor = correspondencias_web_sisepuede[sisepuede_name]

print(f"Processing {sisepuede_name} variable")

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))

relative_path = os.path.normpath(dir_path + "/../raw_data")
relative_path_wbal_file = os.path.join(relative_path, "wbal.csv.tar.bz2")

# Read source data
wbal = pd.read_csv(relative_path_wbal_file, encoding = "ISO-8859-1")
wbal = wbal.rename(columns =
                            {"wbal.csv" : "COUNTRY"}
                            )

# Compute Total Exports of fuel in PJ from a country
wbal_process = wbal.query("FLOW=='Production' and UNIT=='TJ'")[["COUNTRY", "TIME"]].reset_index(drop = True)

wbal_process[sisepuede_name] = wbal.query("FLOW=='Exports' and UNIT=='TJ'")[variable_to_process].reset_index(drop = True)
wbal_process[sisepuede_name] = wbal_process[sisepuede_name].apply(lambda x: float(str(x).replace("..","0").replace('c',"0").replace("x","0")))*factor

# Convert to TeraJoul to PetaJoul
wbal_process[sisepuede_name] = wbal_process[sisepuede_name]*-0.001
wbal_process[sisepuede_name] = wbal_process[sisepuede_name].replace({-0.0 : 0.0})

wbal_process = wbal_process.dropna().reset_index(drop = True)

# Get countries ISO 3 codes
relative_path_iso3_file = os.path.join(relative_path, "iso3_all_countries.csv")
iso3_countries = pd.read_csv(relative_path_iso3_file)

wbal_process["COUNTRY"] = wbal_process["COUNTRY"].replace({'Bolivarian Republic of Venezuela': "Venezuela",
                                                            'Plurinational State of Bolivia' : "Bolivia"})


wbal_process = wbal_process[wbal_process["COUNTRY"].isin(iso3_countries["Category Name"])]
wbal_process = wbal_process.query("COUNTRY !='World'")


# Merge with  ISO 3 codes
wbal_process = wbal_process.rename(columns = {"COUNTRY":"Category Name"})\
         .merge(right = iso3_countries, how = "left", on = "Category Name")

wbal_process = wbal_process[["REGION", "ISO3", "TIME", sisepuede_name]]
wbal_process["TIME"] = wbal_process["TIME"].apply(lambda x: int(x))

wbal_process = wbal_process.rename(columns = {"REGION" : "Nation",
                                          "TIME" : "Year",
                                          "ISO3" : "iso_code3"})

# Get countries without values
latam_countries = set(iso3_countries["REGION"][:26])
non_values = latam_countries.symmetric_difference(latam_countries.intersection(wbal_process["Nation"]))
 
# Impute values with the Costa Rica values
save_df = []
impute_country_base = wbal_process.query(f"Nation == 'costa_rica'").reset_index(drop = True)

for country in non_values:
    impute_country = impute_country_base.copy()
    impute_country["Nation"]= country
    ISO3 , Code = iso3_countries.loc[iso3_countries["REGION"]==country, ["ISO3","Code"]].values[0]
    impute_country["iso_code3"]= ISO3
    impute_country["Code"]= Code
    impute_country["sisepuede_name"] = 0 

    save_df.append(impute_country)


wbal_var_to_proc_all = pd.concat([wbal_process]+save_df, ignore_index = True)
wbal_var_to_proc_all.sort_values(["Nation","Year"], inplace = True)

## Save historical data

wbal_var_to_proc_all.rename(columns = {"ISO3":"iso_code3"}, inplace = True)

relative_path_to_save_historical = os.path.normpath(dir_path + "/../input_to_sisepuede/historical")

relative_path_to_save_historical_file = os.path.join(relative_path_to_save_historical, f"{sisepuede_name}.csv")

wbal_var_to_proc_all[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_historical_file, index = False)

## Get the last one historical year
last_one_year = int(max(wbal_var_to_proc_all["Year"]))
loy_wbal_var_to_proc_all = wbal_var_to_proc_all.query(f"Year=={last_one_year-1}").reset_index(drop=True)

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
