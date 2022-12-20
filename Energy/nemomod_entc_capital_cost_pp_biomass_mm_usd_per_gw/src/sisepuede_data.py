import os 
import tabula
import numpy as np
import pandas as pd

from utils import build_data_frame


# Set directories
#dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","sources" ))
electric_cost_pdf_path = os.path.join(sources_path,"Projected-Costs-of-Generating-Electricity-2020.pdf")

save_path = os.path.abspath(os.path.join(dir_path,"..","output" ))

## SISEPUEDE variables info
sisepuede_vars = {
        "nemomod_entc_capital_cost_pp_biogas_mm_usd_per_gw" : "NO",
        "nemomod_entc_capital_cost_pp_biomass_mm_usd_per_gw" : ("biomass", "55", 1, "Table 3.7b: Other renewable generating technologies – Biomass"),
        "nemomod_entc_capital_cost_pp_coal_mm_usd_per_gw" : ("coal", "51", 0, "Table 3.3: Coal-fired generating technologies"),
        "nemomod_entc_capital_cost_pp_gas_mm_usd_per_gw" : ("gas", "50", 0, "Table 3.2a: Combined-cycle gas turbine (CCGT) generating technology"),
        "nemomod_entc_capital_cost_pp_geothermal_mm_usd_per_gw" : ("geothermal", "56", 0, "Table 3.7c: Other renewable generating technologies – Geothermal"),
        "nemomod_entc_capital_cost_pp_hydropower_mm_usd_per_gw" : ("hydropower", "55", 0, "Table 3.7a: Other renewable generating technologies – Hydropower"),
        "nemomod_entc_capital_cost_pp_nuclear_mm_usd_per_gw" : ("nuclear", "51", 1, "Table 3.4a: Nuclear generating technologies – New build"),
        "nemomod_entc_capital_cost_pp_ocean_mm_usd_per_gw" : "NO",
        "nemomod_entc_capital_cost_pp_oil_mm_usd_per_gw" : "NO",
        "nemomod_entc_capital_cost_pp_solar_mm_usd_per_gw" : ("solar", "52-53", 0, "Table 3.5: Solar generating technologies"),
        "nemomod_entc_capital_cost_pp_waste_incineration_mm_usd_per_gw" : "NO",
        "nemomod_entc_capital_cost_pp_wind_mm_usd_per_gw" : ("wind", "53-54", 1, "Table 3.6a: Wind generating technology – Onshore")
    }

columns_info = {"biomass" : {"Country" : str,
                            "Technology" : str,
                            "Net capacity (MWe)": float,
                            "Capacity factor (%)": float,
                            "Overnight costs (USD/kWe)" : int,
                            "Investment costs (USD/kWe) 3%" : int,
                            "Investment costs (USD/kWe) 7%" : int,
                            "Investment costs (USD/kWe) 10%" : int},

                 "coal" : {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Electrical conversion efficiency (%)": float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int},

                  "gas": {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Electrical conversion efficiency (%)": float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int},

                  "geothermal" : {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Capacity factor (%)": float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int},

                   "hydropower" : {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Capacity factor (%)": float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int},

                   "nuclear" : {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int}, 

                  "solar" : {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Capacity factor (%)": float,
                        "Annual efficiency loss (%)" : float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int},

                   "wind" : {"Country" : str,
                        "Technology" : str,
                        "Net capacity (MWe)": float,
                        "Capacity factor (%)": float,
                        "Overnight costs (USD/kWe)" : int,
                        "Investment costs (USD/kWe) 3%" : int,
                        "Investment costs (USD/kWe) 7%" : int,
                        "Investment costs (USD/kWe) 10%" : int}                    
                }


#### Test execution
var_short, pages, table_num, table_name = sisepuede_vars["nemomod_entc_capital_cost_pp_gas_mm_usd_per_gw"]


# Read page into list of DataFrame
dfs = tabula.read_pdf(electric_cost_pdf_path, pages=pages, lattice=True)

# Get Table 
table_row = dfs[table_num] 

# Use only necessary information and transform to numpy array
table_np = table_row.iloc[2:,].to_numpy().T

dict_data_type = columns_info[var_short]

df_table = build_data_frame(table_np, dict_data_type)

table_name_file = table_name.replace(" ","_") + ".csv"
file_df_table = os.path.join(save_path, table_name_file)


### Run for all variables

acumula_df_variables = {}

for k,v in sisepuede_vars.items():
    
    if v!="NO":

        print(f"Processing {k}")

        var_short, pages, table_num, table_name = sisepuede_vars[k]
        dict_data_type = columns_info[var_short]

        if "-" in pages:
            pages_list = pages.split("-")
            acumula_df = []
            for index, page in enumerate(pages_list):
                
                if index == 0:
                    # Break data frame

                    # First data frame
                    # Read page into list of DataFrame
                    dfs = tabula.read_pdf(electric_cost_pdf_path, pages = page, lattice=True)

                    # Get Table 
                    table_row = dfs[table_num] 

                    if var_short == "solar":
                        final_index = 38
                    elif var_short == "wind":
                        final_index = 33
                    
                    # Use only necessary information and transform to numpy array
                    table_np = table_row.iloc[2:final_index,].to_numpy().T


                    df_table = build_data_frame(table_np, dict_data_type)

                    acumula_df.append(df_table.copy())

                    # Second data frame

                    table_np = table_row.iloc[final_index+1:,range(len(table_np)-1)].to_numpy().T

                    country_np = np.array(["United States" for i in range(table_np.shape[1])])

                    table_np = np.vstack((country_np,table_np))

                    df_table = build_data_frame(table_np, dict_data_type)

                    acumula_df.append(df_table.copy())
                else:

                    # Read page into list of DataFrame
                    dfs = tabula.read_pdf(electric_cost_pdf_path, pages = page, lattice=True)

                    # Get Table 
                    table_row = dfs[0] 

                    # Use only necessary information and transform to numpy array
                    table_np = table_row.iloc[2:,].to_numpy().T


                    df_table = build_data_frame(table_np, dict_data_type)

                    acumula_df.append(df_table.copy())

            table_name_file = table_name.replace(" ","_") + ".csv"
            file_df_table = os.path.join(save_path, table_name_file)

            df_table_all = pd.concat(acumula_df, ignore_index = True)

            df_table_all.to_csv(file_df_table, index = False)

            acumula_df_variables[var_short] = df_table[["Country", "Investment costs (USD/kWe) 10%"]].groupby("Country").mean()

        else:

            # Read page into list of DataFrame
            dfs = tabula.read_pdf(electric_cost_pdf_path, pages=pages, lattice=True)

            # Get Table 
            table_row = dfs[table_num] 

            # Use only necessary information and transform to numpy array
            if var_short == "coal":
                table_np = table_row.iloc[2:table_np.shape[1]-1,].to_numpy().T
            else:
                table_np = table_row.iloc[2:,].to_numpy().T


            df_table = build_data_frame(table_np, dict_data_type)

            table_name_file = table_name.replace(" ","_") + ".csv"
            file_df_table = os.path.join(save_path, table_name_file)

            df_table.to_csv(file_df_table, index = False)
            
            acumula_df_variables[var_short] = df_table[["Country", "Investment costs (USD/kWe) 10%"]].groupby("Country").mean()

## Load ISO3 codes

iso3_code_path = os.path.join(sources_path,"iso3_countries.csv")

iso3_code = pd.read_csv(iso3_code_path)

iso3_code = iso3_code[["Continent", "Name", "ISO 3"]]


dict_rename_country = {'Korea' : 'Korea, Republic of',
                        'Russia' : 'Russian Federation',
                        'Slovak Republic' : 'Slovakia'}

for k,v in acumula_df_variables.items():
    print("++++++++++++++++++++++++++++")
    print(k)
    print("++++++++++++++++++++++++++++")

    for country in v.index:
        iniso = country in list(iso3_code["Name"])
        print(f"{country} in iso? {iniso}")

        if not iniso:
            if country != "Geothermal":
                v.rename(index={country : dict_rename_country[country]}, inplace = True)

continent_value = {}
iso3_code.rename(columns = {"Name": "Country"}, inplace = True)

for k,v in acumula_df_variables.items():
    v.reset_index(inplace = True)
    v.query("Country != 'Geothermal'", inplace = True)

    continent_value[k] = v.merge(right = iso3_code, how = "inner", on = "Country")
    continent_value[k] = continent_value[k][["Continent","Investment costs (USD/kWe) 10%"]].groupby("Continent").mean()
    v.set_index("Country", inplace = True)

world_value = {}
for k,v in acumula_df_variables.items():
    world_value[k] = continent_value[k]["Investment costs (USD/kWe) 10%"].mean() 


iso3_code.set_index("Country", inplace = True)

init_year = 2000
final_year = 2051

total_years = len(range(init_year, final_year))

dict_vars_sisepuede = {}

for k,v in acumula_df_variables.items():
    print("++++++++++++++++++++++++++++")
    print(k)
    print("++++++++++++++++++++++++++++")

    acumula_var_sisepuede = []

    for country in iso3_code.index:

        continent_of_country = iso3_code.loc[country]["Continent"]     

        capital_cost = 0
        
        # Country is in original data?
        
        if country in list(v.index):
            capital_cost = v.loc[country, "Investment costs (USD/kWe) 10%"]
        
        # If not, check continental value        
        elif continent_of_country in list(continent_value[k].index):
            capital_cost = continent_value[k].loc[continent_of_country, "Investment costs (USD/kWe) 10%"]

        else:
            capital_cost = world_value[k]


        for var_sisepuede in sisepuede_vars.keys():
            if k in var_sisepuede:
                to_save_var_sisepuede = var_sisepuede

        country_var_sisepuede = pd.DataFrame({"Nation" : [country] * total_years,
                      "iso_code3" : [iso3_code.loc[country,"ISO 3"]] * total_years,
                      "Year" : range(init_year, final_year),
                       to_save_var_sisepuede : [capital_cost] * total_years})

        acumula_var_sisepuede.append(country_var_sisepuede)

    dict_vars_sisepuede[to_save_var_sisepuede] = pd.concat(acumula_var_sisepuede, ignore_index = True)

    file_df_table = os.path.join(save_path, to_save_var_sisepuede +".csv")

    dict_vars_sisepuede[to_save_var_sisepuede].to_csv(file_df_table, index = False)
