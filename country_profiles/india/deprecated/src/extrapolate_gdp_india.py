import pandas as pd 

initial_year = 2015
final_year = 2070

reference_scenario = [2.10, 2.67, 3.24, 4.34, 5.90, 7.99, 10.64, 13.94, 18.04, 23.11, 29.32, 36.9]
aspirational_scenario = [2.10, 2.67, 3.26, 4.51, 6.54, 9.83, 15.40, 23.73, 33.94, 45.23, 56.12, 64.75]

reference_scenario = [i*1000 for i in reference_scenario]
aspirational_scenario = [i*1000 for i in aspirational_scenario]

time_period = range(initial_year, final_year+5, 5)

df_original = pd.DataFrame(
    {
        "reference_scenario" : reference_scenario,
        "aspirational_scenario" : aspirational_scenario
    },
    index = time_period
)

df_interpolado = pd.DataFrame(index = range(initial_year, final_year+1))

df_interpolado = pd.concat([df_interpolado, df_original], axis = 1).interpolate()

df_interpolado = df_interpolado.T.reset_index()

df_interpolado = df_interpolado.rename(columns = {"index" : "gdp_india"})

df_interpolado.to_excel("gdp_india_reference_aspirational.xlsx", index = False)