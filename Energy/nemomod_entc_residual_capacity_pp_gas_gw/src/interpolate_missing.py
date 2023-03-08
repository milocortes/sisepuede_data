import pandas as pd
import os 
import sys


# Get Coal and coal products import data
sisepuede_name = sys.argv[1]
print(f"Processing {sisepuede_name} variable")

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

relative_path_historical_data = os.path.normpath(dir_path + "/../input_to_sisepuede/historical")
relative_path_projected_data = os.path.normpath(dir_path + "/../input_to_sisepuede/projected")

relative_path_historical_file = os.path.join(relative_path_historical_data, f"{sisepuede_name}.csv")
relative_path_projected_file = os.path.join(relative_path_projected_data, f"{sisepuede_name}.csv")

# Load historical and projected data

all_period_df = pd.concat(
    [pd.read_csv(relative_path_historical_file), pd.read_csv(relative_path_projected_file)],
    ignore_index = True
)


#### Interpolamos los datos a los países con missing values EN SU RANGO ORIGINAL

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print(" Interpolamos los datos a los países con missing values EN SU RANGO ORIGINAL ")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

periodo_suficiente = list(range(1990, 2051))
acumula_missing_country = []
dfs_interpolates = []

for nation in all_period_df.Nation.unique():

    df_test_nation = all_period_df.query(f"Nation =='{nation}'")
    years_nation = df_test_nation["Year"].to_list()
    test_iso_code3_country = df_test_nation.iso_code3.unique()[0]

    ### Interpolamos los datos a los países con missing values EN SU RANGO ORIGINAL
    min_year = min(years_nation)
    max_year = max(years_nation)

    # ¿Tiene missing en su rango original?
    if not set(range(min_year, max_year+1)).issubset(years_nation):
        anios_faltantes_entre = set(range(min_year, max_year+1)).symmetric_difference(set(years_nation).intersection(range(min_year, max_year+1)))
        print(f"** {nation} **  cumple el periodo suficiente, pero tiene missing entre sus valores.\nLe faltan los anios\n{anios_faltantes_entre}")
        acumula_missing_country.append(nation)
        completo = pd.DataFrame(index = range(min_year, max_year+1))
        completo = pd.concat([completo, df_test_nation.set_index("Year")], axis = 1)
        completo.index.set_names(['Year'], inplace = True)
        completo.reset_index(inplace = True)
        completo = completo.interpolate().fillna(method='bfill')
        completo["Nation"] = nation
        completo["iso_code3"] = test_iso_code3_country
        dfs_interpolates.append(completo.copy())
    
all_period_df.sort_values(["Nation","Year"], inplace = True)  

## Quitamos los paises con valores faltantes para agregarlos nuevamente con los valores interpolados
all_period_df = all_period_df[~all_period_df["Nation"].isin(acumula_missing_country)] 
all_period_df = pd.concat([all_period_df] + dfs_interpolates, ignore_index = True).reset_index(drop = True)

##### Interpolamos los datos a los países con missing values EN EL PERIODO SUFICIENTE
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print(" Interpolamos los datos a los países con missing values EN EL PERIODO SUFICIENTE")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

periodo_suficiente = list(range(1990, 2051))
acumula_missing_country = []
dfs_interpolates = []

for nation in all_period_df.Nation.unique():

    df_test_nation = all_period_df.query(f"Nation =='{nation}'")
    years_nation = df_test_nation["Year"].to_list()
    test_iso_code3_country = df_test_nation.iso_code3.unique()[0]

    ### Interpolamos los datos a los países con missing values EN EL PERIODO SUFICIENTE
    if not set(periodo_suficiente).issubset(years_nation):
        print(f"** {nation} **  NO cumple el periodo suficiente.")

        acumula_missing_country.append(nation)
        completo = pd.DataFrame(index = periodo_suficiente)
        completo = pd.concat([completo, df_test_nation.set_index("Year")], axis = 1)
        completo.index.set_names(['Year'], inplace = True)
        completo.reset_index(inplace = True)
        completo = completo.interpolate().fillna(method='bfill')
        completo["Nation"] = nation
        completo["iso_code3"] = test_iso_code3_country
        dfs_interpolates.append(completo.copy())

    
all_period_df.sort_values(["Nation","Year"], inplace = True)  

## Quitamos los paises con valores faltantes para agregarlos nuevamente con los valores interpolados
all_period_df = all_period_df[~all_period_df["Nation"].isin(acumula_missing_country)] 
all_period_df = pd.concat([all_period_df] + dfs_interpolates, ignore_index = True).reset_index(drop = True)

## Save interpolated historical data
all_period_df.query("Year <=2020").to_csv(relative_path_historical_file, index = False)
## Save interpolated projected data
all_period_df.query("Year >2020").to_csv(relative_path_projected_file, index = False)