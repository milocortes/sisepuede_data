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

# Read 55 page into list of DataFrame
dfs = tabula.read_pdf(electric_cost_pdf_path, pages='55', lattice=True)

# Get Table 3.7a: Other renewable generating technologies – Hydropower (the first one table)
table_3_7_a_row = dfs[0] 

# Use only necessary information and transform to numpy array
table_3_7_a_row_np = table_3_7_a_row.iloc[2:,].to_numpy().T


# Convert table_3_7_a_row_np to pandas data frame

# Define columns and types
dict_data_type = {"Country" : str,
                  "Technology" : str,
                  "Net capacity (MWe)": float,
                  "Capacity factor (%)": float,
                  "Overnight costs (USD/kWe)" : int,
                  "Investment costs (USD/kWe) 3%" : int,
                  "Investment costs (USD/kWe) 7%" : int,
                  "Investment costs (USD/kWe) 10%" : int}


df_table_3_7_a = build_data_frame(table_3_7_a_row_np, dict_data_type)
df_table_3_7_a

# Save data
file_df_table_3_7_a = os.path.join(save_path, "df_table_3_7_a.csv")
df_table_3_7_a.to_csv(file_df_table_3_7_a, index = False)

# Convert Table 3.7b: Other renewable generating technologies – Biomass
# Get Table 
table_3_7_b_row = dfs[1] 

# Use only necessary information and transform to numpy array
table_3_7_b_row_np = table_3_7_b_row.iloc[2:,].to_numpy().T

df_table_3_7_b = build_data_frame(table_3_7_b_row_np, dict_data_type)
df_table_3_7_b

# Save data
file_df_table_3_7_b = os.path.join(save_path, "df_table_3_7_b.csv")
df_table_3_7_b.to_csv(file_df_table_3_7_b, index = False)

## Convert Table 3.5: Solar generating technologies (page 50)

# Read 50 page into list of DataFrame
dfs = tabula.read_pdf(electric_cost_pdf_path, pages='52', lattice=True)

# Get Table 3.5
table_3_5_row = dfs[0] 

# Problema: se desplaza una columna a la izquierda en el registro de EUA
# Solución: parte en dos el data frame

# Primer data frame
# Use only necessary information and transform to numpy array
table_3_5_row_np = table_3_5_row.iloc[2:38,].to_numpy().T

# Define columns and types
dict_data_type = {"Country" : str,
                  "Technology" : str,
                  "Net capacity (MWe)": float,
                  "Capacity factor (%)": float,
                  "Annual efficiency loss (%)" : float,
                  "Overnight costs (USD/kWe)" : int,
                  "Investment costs (USD/kWe) 3%" : int,
                  "Investment costs (USD/kWe) 7%" : int,
                  "Investment costs (USD/kWe) 10%" : int}

df_table_3_5_primero = build_data_frame(table_3_5_row_np, dict_data_type)
df_table_3_5_primero

# Segundo data frame
table_3_5_row_np = table_3_5_row.iloc[38:,range(len(table_3_5_row_np)-1)].to_numpy().T

country_np = np.array(["United States" for i in range(table_3_5_row_np.shape[1])])

table_3_5_row_np = np.vstack((country_np,table_3_5_row_np))

df_table_3_5_segundo = build_data_frame(table_3_5_row_np, dict_data_type)
df_table_3_5_segundo

df_table_3_5 = pd.concat([df_table_3_5_primero, df_table_3_5_segundo], ignore_index = True)
df_table_3_5

# Save data
file_df_table_3_5 = os.path.join(save_path, "df_table_3_5.csv")
df_table_3_5.to_csv(file_df_table_3_5, index = False)