import numpy as np
import pandas as pd

from typing import List, Dict


def convert_to_float(input_value : str) -> float:
    if isinstance(input_value, str):
        input_value = float(input_value.replace(" ","").replace("%",""))
        return input_value
    else:
         return 0.0

def convert_to_int(input_value : str) -> int:
    if isinstance(input_value, str):
        input_value = int(input_value.replace(" ",""))
        return input_value
    else:
         return 0

def complete_countries(row_data : np.array) -> List[str]:

    impute_countries = []
    actual_country = None

    for country in row_data:
        if isinstance(country, str):
            actual_country = country
            impute_countries.append(actual_country)
        else:
            impute_countries.append(actual_country)

    return impute_countries

def build_data_frame(row_data : np.array, columns_info : Dict) -> pd.DataFrame:
    
    """
    build_data_frame function

    Args:

        * row_data (np.array):  Information table
        * columns_info (Dict): Dictionary with columns names and data type
    """

    dict_columns_data ={}

    for i, (col_name,col_type) in enumerate(columns_info.items()):
        if col_name == "Country":
            impute_countries = complete_countries(row_data[i])
            dict_columns_data[col_name] = impute_countries

        elif col_type == str:
            dict_columns_data[col_name] = row_data[i]

        elif col_type == float:
            dict_columns_data[col_name] = [convert_to_float(v) for v in row_data[i]]
        
        elif col_type == int:
            dict_columns_data[col_name] = [convert_to_int(v) for v in row_data[i]]


    df_columns_data = pd.DataFrame(dict_columns_data)

    # Remove Non-OECD countries register
    df_columns_data = df_columns_data.query("Country != 'Non-OECD countries'")
    
    return df_columns_data
