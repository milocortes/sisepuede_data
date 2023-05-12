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


wbal["COUNTRY"] = wbal["COUNTRY"].replace({'Bolivarian Republic of Venezuela': "Venezuela, RB",
                                                            'Plurinational State of Bolivia' : "Bolivia",
                                                            'Turkey' : 'Turkiye',
                                                            'China (P.R. of China and Hong Kong, China)' : "China",
                                                            "Democratic People's Republic of Korea" : "Korea, Dem. People's Rep.",
                                                            "Czech Republic": "Czechia",
                                                            "Côte d'Ivoire": "Cote d'Ivoire",
                                                            'Democratic Republic of the Congo': "Congo, Dem. Rep.",
                                                            'Egypt' : "Egypt, Arab Rep.",
                                                            'Islamic Republic of Iran': "Iran, Islamic Rep.",
                                                            'Korea' : "Korea, Rep.",
                                                            'Viet Nam' : "Vietnam", 
                                                            'Yemen' : "Yemen, Rep.",
                                                            'Hong Kong (China)' : 'Hong Kong SAR, China'})
# Compute Domestic Demand:
# (Production + Imports = Domestic_Demand + Exports)

wbal_process = wbal.query("FLOW=='Production' and UNIT=='TJ'")[["COUNTRY", "TIME"]].reset_index(drop = True)
wbal_process["Total final consumption"] = wbal.query("FLOW=='Total final consumption' and UNIT=='TJ'")[variable_to_process].reset_index(drop = True)
wbal_process["Production"] = wbal.query("FLOW=='Production' and UNIT=='TJ'")[variable_to_process].reset_index(drop = True)
wbal_process["Imports"] = wbal.query("FLOW=='Imports' and UNIT=='TJ'")[variable_to_process].reset_index(drop = True)
wbal_process["Exports"] = wbal.query("FLOW=='Exports' and UNIT=='TJ'")[variable_to_process].reset_index(drop = True)

for colvar in ["Total final consumption", "Production","Imports", "Exports"]:
    wbal_process[colvar] = wbal_process[colvar].apply(lambda x: float(str(x).replace("..","0").replace('c',"0").replace("x","0")))*factor

wbal_process["domestic_demand"] = wbal_process["Total final consumption"] + wbal_process["Production"] - wbal_process["Exports"] + wbal_process["Imports"]

wbal_process[sisepuede_name] = wbal_process["Imports"]/wbal_process["domestic_demand"]

## Nos quedamos sólo con los Total final consumption distintos a cero
wbal_process = wbal_process.dropna().reset_index(drop = True)

# Get countries ISO 3 codes
relative_path_iso3_file = os.path.join(relative_path, "wb_regionalization.csv")
iso3_countries = pd.read_csv(relative_path_iso3_file)

wbal_process = wbal_process[wbal_process["COUNTRY"].isin(iso3_countries["Nation"])]
wbal_process = wbal_process.query("COUNTRY !='World'")


# Merge with  ISO 3 codes
wbal_process = wbal_process.rename(columns = {"COUNTRY":"Nation"})\
         .merge(right = iso3_countries, how = "left", on = "Nation")

wbal_process = wbal_process[["Nation", "iso_code3", "TIME", sisepuede_name]]
wbal_process["TIME"] = wbal_process["TIME"].apply(lambda x: int(x))

wbal_process = wbal_process.rename(columns = {"REGION" : "Nation",
                                          "TIME" : "Year",
                                          "ISO3" : "iso_code3"})

# Get countries without values
latam_countries = set(iso3_countries["Nation"][:26])
non_values = latam_countries.symmetric_difference(latam_countries.intersection(wbal_process["Nation"]))
 
# Impute values with the Costa Rica values
save_df = []
impute_country_base = wbal_process.query(f"iso_code3 == 'CRI'").reset_index(drop = True)

for country in non_values:
    impute_country = impute_country_base.copy()
    impute_country["Nation"]= country
    ISO3  = iso3_countries.loc[iso3_countries["Nation"]==country, "iso_code3"].values[0]
    impute_country["iso_code3"]= ISO3
    impute_country["sisepuede_name"] = 0 

    save_df.append(impute_country)


wbal_var_to_proc_all = pd.concat([wbal_process]+save_df, ignore_index = True)
wbal_var_to_proc_all.sort_values(["Nation","Year"], inplace = True)

## Save historical data

wbal_var_to_proc_all.rename(columns = {"ISO3":"iso_code3"}, inplace = True)

relative_path_to_save_historical = os.path.normpath(dir_path + "/../input_to_sisepuede/historical")

relative_path_to_save_historical_file = os.path.join(relative_path_to_save_historical, f"{sisepuede_name}.csv")

wbal_var_to_proc_all[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_historical_file, index = False)

## Get the last one historical year for each country
acumula_df_todos = []

for country in wbal_var_to_proc_all.Nation.unique():
    
    #last_one_year = int(max(wbal_var_to_proc_all.query(f"Nation=='{country}'")["Year"]))
    #loy_wbal_var_to_proc_all = wbal_var_to_proc_all.query(f"Nation=='{country}' and Year=={last_one_year-1}").reset_index(drop=True)

    last_one_year = int(max(wbal_var_to_proc_all.query(f'Nation=="{country}"')["Year"]))
    loy_wbal_var_to_proc_all = wbal_var_to_proc_all.query(f'Nation=="{country}" and Year=={last_one_year-1}').reset_index(drop=True)

    ## Project with the last value to 2050

    acumula_df = []

    for i in range(last_one_year, 2050):
        last_one_year += 1
        new_loy_df = loy_wbal_var_to_proc_all.copy()
        new_loy_df["Year"] = last_one_year
        acumula_df.append(new_loy_df)

    df_project = pd.concat(acumula_df, ignore_index = True)

    acumula_df_todos.append(df_project)

acumula_df_todos = pd.concat(acumula_df_todos, ignore_index = True)
acumula_df_todos.sort_values(["Nation","Year"], inplace = True)

## Save projected data

relative_path_to_save_projected = os.path.normpath(dir_path + "/../input_to_sisepuede/projected")

relative_path_to_save_projected_file = os.path.join(relative_path_to_save_projected, f"{sisepuede_name}.csv")

acumula_df_todos[["Year", "Nation","iso_code3",sisepuede_name]].to_csv(relative_path_to_save_projected_file, index = False)
