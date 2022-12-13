import pandas as pd
import glob

sectores = ['AFOLU','all_sectors','CircularEconomy','IPPU']

fake_data_complete = pd.read_csv("https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/fake_data/fake_data_complete.csv")
df_var_complete = fake_data_complete.columns[1:]

ac_variables = []
ac_sectores = []
ac_in_inputs = []
ac_init_year = []
ac_final_year = []
ac_var_change_time = []

for sector in sectores:
    print("\n\n{}\n\n".format(sector))

    archivos_sector = [i.split("/")[1].split(".")[0] for i in glob.glob("{}/*.csv".format(sector))]
    ac_variables += archivos_sector
    ac_sectores += [sector] * len(archivos_sector)
    ac_in_inputs += [1 if i in df_var_complete else 0 for i in archivos_sector]

    for archivo in archivos_sector:
        print(archivo)
        df_var = pd.read_csv("{}/{}.csv".format(sector,archivo))
        init_year = min(df_var["Year"])
        final_year = max(df_var["Year"])
        ac_init_year.append(init_year)
        ac_final_year.append(final_year)

        if init_year == final_year:
            ac_var_change_time.append(0)
        else:
            ac_var_change_time.append(1)

resumen = pd.DataFrame({"variable" : ac_variables,
                        "sector" : ac_sectores,
                        "in_inputs" : ac_in_inputs,
                        "init_year" : ac_init_year,
                        "final_year" : ac_final_year,
                        "var_change_time" : ac_var_change_time})

resumen.sort_values(by=['sector','variable'],inplace=True)
resumen.to_csv("resumen_variables_observadas.csv", index = False)
