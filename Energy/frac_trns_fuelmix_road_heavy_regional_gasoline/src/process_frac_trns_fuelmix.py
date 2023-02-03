import os 
import tabula
import numpy as np
import pandas as pd

# Set directories
#dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data","pdfs" ))


pages_tables = [56, 57, 59, 59, 59, 63, 61, 61, 61, 61, 61, 61]
editions = range(29, 41)
years = range(2008, 2020)

columns_name = ["transportation_mode", "gasoline", "diesel_fuel", "liquefied_petroleum_gas", "jet_fuel", "residual_fuel_oil", "natural_gas", "electricity", "total"]

correspondence_tables = {(year,edition) : page for page, year, edition in zip(pages_tables, editions, years)}
dfs_anios = {}

fuel_types = ['gasoline', 'diesel_fuel', 'liquefied_petroleum_gas', 'jet_fuel', 'residual_fuel_oil', 'natural_gas', 'electricity']

for (edition, year), page in correspondence_tables.items():

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Processing Page :{page}- Year : {year}- Edition : {edition}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    transportation_energy_pdf_path = os.path.join(sources_path,f"tedb_edition{edition}.pdf")

    dfs = tabula.read_pdf(transportation_energy_pdf_path, pages=f'{page}', relative_area=True, stream=True)
    df_information = dfs[0]
    df_information = df_information[2:-2].fillna(0).replace("-",0) 
    df_information.rename(columns = {old:new for old,new in zip(df_information.columns, columns_name)}, inplace = True)
    
    df_information["total"] = df_information["total"].str.replace(",","").astype(float)

    # Fix to numeric data type
    for fuel in fuel_types:
        df_information[fuel] = df_information[fuel].str.replace("c","NaN")
        df_information[fuel] = df_information[fuel].str.replace(",", "").astype(float)

    # Natural Gas is equal to natural_gas plus liquefied_petroleum_gas
    df_information.fillna(0, inplace = True)
    df_information["natural_gas"] = df_information["natural_gas"] + df_information["liquefied_petroleum_gas"] 

    """
    for fuel in fuel_types:
        df_information[fuel] = df_information[fuel]/df_information["total"] 
        df_information[fuel] = df_information[fuel].round(3)
    """

    df_information = df_information[["transportation_mode"] + fuel_types].fillna(0)
    df_information["transportation_mode"] = df_information["transportation_mode"].str.lower()
    dfs_anios[year] = df_information.set_index("transportation_mode")
    

### Correspondence with SISEPUEDE


datos_lac = pd.read_csv( os.path.abspath(os.path.join(dir_path,"..","raw_data","datos_energia_lac.csv" )))  

frac_trns_variables = [i for i in datos_lac["Variable"] if "frac_trns_fuelmix" in i]  

frac_trns_var_no_fuel = ["aviation", "powered_bikes", "public", "rail_freight", "rail_passenger", "road_heavy_freight", "road_heavy_regional", "road_light", "water_borne"]

fuel_type_corespondence_te_sisepuede = {"gasoline" : "gasoline",  "diesel" : "diesel_fuel", "natural_gas" : "natural_gas", "electricity" : "electricity"}


transportation_mode_corr_te_sisepuede = {"buses" : "public" , "medium/heavy trucks" : "road_heavy_freight", "passenger" : "rail_passenger", 
                                         "light vehicles" : "road_light", "freight" : "water_borne"}


save_dfs_by_transport_type = {f"frac_trns_fuelmix_{v}": {} for k,v in transportation_mode_corr_te_sisepuede.items()}

for trans_type_trns, trans_type_sise  in  transportation_mode_corr_te_sisepuede.items():
    print(trans_type_trns)
    all_trans_type_sise = [i for i in frac_trns_variables if trans_type_sise in i]

    if trans_type_sise == "public":
        print(all_trans_type_sise)

    for fuel_type_sisepuede, fuel_type_trns in fuel_type_corespondence_te_sisepuede.items():

        var_sisepuede_to_build = [i for i in all_trans_type_sise if fuel_type_sisepuede in i]

        if fuel_type_sisepuede=="electricity":
            var_sisepuede_to_build
            
        if var_sisepuede_to_build:

            var_sisepuede_to_build = var_sisepuede_to_build[0]
            years_to_df = []
            values_to_df = []

            for year, df_trns in dfs_anios.items():
                values_to_df.append(df_trns.loc[trans_type_trns,fuel_type_trns])
                years_to_df.append(year)

            all_trans_type_sise.remove(var_sisepuede_to_build)

            df_var_sisepuede_to_build = pd.DataFrame({"Year" : years_to_df, var_sisepuede_to_build : values_to_df})
            save_dfs_by_transport_type[f"frac_trns_fuelmix_{trans_type_sise}"][var_sisepuede_to_build] = df_var_sisepuede_to_build


    for resto_var_sisepuede in all_trans_type_sise:
        time_period = range(2008, 2020)
        df_var_sisepuede_to_build = pd.DataFrame({"Year" : time_period, resto_var_sisepuede : [0.0]*len(time_period)})
        save_dfs_by_transport_type[f"frac_trns_fuelmix_{trans_type_sise}"][resto_var_sisepuede] = df_var_sisepuede_to_build

## Compute shares by each mode of trasnportation
time_period = range(2008, 2020)

for k, v in save_dfs_by_transport_type.items(): 
    
    total = pd.Series([0.0]*len(time_period))
    
    for var_sise, df_sise in v.items():
        total += df_sise[var_sise]

    for var_sise, df_sise in v.items():
        df_sise[var_sise] = df_sise[var_sise]/total

## Test sum equal to 1 for each transport_type

for transport_type, dfs_transpot_type  in save_dfs_by_transport_type.items():
    print(transport_type)

    checa_suma = pd.DataFrame({"Year":range(2008,2020)})

    for var_sisepuede, df_var_sisepuede in dfs_transpot_type.items():
        checa_suma[var_sisepuede] = df_var_sisepuede[var_sisepuede]

    #print(checa_suma)
    print("SUMA")
    print(checa_suma[dfs_transpot_type.keys()].sum(axis=1))

## Save all variables
save_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ,"USA_transportation_energy_data" )) 

for transport_type, dfs_transpot_type  in save_dfs_by_transport_type.items():
    print(transport_type)

    for var_sisepuede, df_var_sisepuede in dfs_transpot_type.items():
        file_name_to_save = f"{var_sisepuede}.csv"
        file_name_to_save_path = os.path.join(save_path, file_name_to_save)
        df_var_sisepuede.to_csv(file_name_to_save_path, index =False)
