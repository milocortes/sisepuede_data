import pandas as pd

wbal = pd.read_csv("../../../wbal.csv")

# Get Natural Gas export data
variable_to_process = "Natural gas"
sisepuede_name = "exports_enfu_pj_fuel_natural_gas"

wbal_var_to_proc = wbal[['COUNTRY','FLOW','TIME','UNIT',variable_to_process]]
wbal_var_to_proc = wbal_var_to_proc.query("FLOW == 'Exports'")

# Get sisepuede_countries_iso3.csv
sisepuede_countries = pd.read_csv("../../../sisepuede_countries_iso3.csv")
wbal_var_to_proc = wbal_var_to_proc[wbal_var_to_proc["COUNTRY"].isin(sisepuede_countries["Category Name"])]

wbal_var_to_proc[variable_to_process] = -1*wbal_var_to_proc[variable_to_process].apply(lambda x: float(str(x).replace("..","0")))

# Assumption export 0.39 of export Natural Gas go to electricity production
# https://www.eia.gov/tools/faqs/faq.php?id=427&t=3
factor = 0.39
wbal_var_to_proc[variable_to_process]  = wbal_var_to_proc[variable_to_process] * factor

# Convert to TeraJoul to PetaJoul
wbal_var_to_proc = wbal_var_to_proc.query("UNIT=='TJ'")
wbal_var_to_proc[variable_to_process]  = wbal_var_to_proc[variable_to_process]*0.001

# Merge with sisepuede_countries
wbal_var_to_proc_merge = wbal_var_to_proc.rename(columns = {"COUNTRY":"Category Name"})\
         .merge(right = sisepuede_countries[["Category Name", "REGION", "ISO3", "Code"]], 
         how = "left", on = "Category Name")

wbal_var_to_proc_merge = wbal_var_to_proc_merge[["REGION", "ISO3", "Code", "TIME", variable_to_process]]

wbal_var_to_proc_merge = wbal_var_to_proc_merge.rename(columns = {"REGION" : "Nation",
                                          "TIME" : "Year",
                                          variable_to_process: sisepuede_name})

# Get countries without values
non_values = list(set(sisepuede_countries["REGION"]).symmetric_difference(wbal_var_to_proc_merge["Nation"]))

# Impute values with the Costa Rica values
save_df = []
impute_country_base = wbal_var_to_proc_merge.query(f"Nation == 'costa_rica'").reset_index(drop = True)

for country in non_values:
    impute_country = impute_country_base.copy()
    impute_country["Nation"]= country
    ISO3 , Code = sisepuede_countries.loc[sisepuede_countries["REGION"]==country, ["ISO3","Code"]].values[0]
    impute_country["ISO3"]= ISO3
    impute_country["Code"]= Code

    save_df.append(impute_country)


wbal_var_to_proc_all = pd.concat([wbal_var_to_proc_merge]+save_df, ignore_index = True)
wbal_var_to_proc_all.sort_values(["Nation","Year"], inplace = True)

## Save historical data
wbal_var_to_proc_all.rename(columns = {"ISO3":"iso_code3"}, inplace = True)
wbal_var_to_proc_all.to_csv(f"../input_to_sisepuede/historical/{sisepuede_name}.csv", index = False)

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
df_project.to_csv(f"../input_to_sisepuede/projected/{sisepuede_name}.csv", index = False)