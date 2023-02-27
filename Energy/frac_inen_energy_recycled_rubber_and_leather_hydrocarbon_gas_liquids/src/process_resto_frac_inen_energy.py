import pandas as pd                                                                                                                                                                                        
import os
import sys 

# Set directories
#dir_path = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))

sources_path = os.path.abspath(os.path.join(dir_path, "..", "raw_data"))

# Load any frac_inen_energy_ variable in order to build templates
historical_template = pd.read_csv("https://raw.githubusercontent.com/milocortes/sisepuede_data/main/Energy/frac_inen_energy_cement_natural_gas/input_to_sisepuede/historical/frac_inen_energy_cement_natural_gas.csv")      
projected_template = pd.read_csv("https://raw.githubusercontent.com/milocortes/sisepuede_data/main/Energy/frac_inen_energy_cement_natural_gas/input_to_sisepuede/projected/frac_inen_energy_cement_natural_gas.csv")      

historical_template = historical_template[["Nation","iso_code3", "Year"]]                                                                                                                                                                    
projected_template = projected_template[["Nation","iso_code3", "Year"]]                                                                                                                                                                    

# Get missing variables of group frac_inen_energy_
all_energy_variables = pd.read_csv(os.path.join(sources_path, "datos_energia_lac.csv"))

with open(os.path.join(sources_path, "frac_inen_energy_variables.txt")) as temp_available_frac_inen_energy:
    available_frac_inen_energy = [f.replace("\n", "") for f in temp_available_frac_inen_energy]

all_frac_inen_energy = [i for i in all_energy_variables["Variable"] if "frac_inen_energy" in i]
missing_frac_inen_energy = list(set(all_frac_inen_energy).symmetric_difference(available_frac_inen_energy))

# Verify if the variable is diferent to zero in fake data 

fake_data = pd.read_csv("https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/fake_data/fake_data_complete.csv")

non_zero_variables = []

for missing_var in missing_frac_inen_energy:
    if fake_data[missing_var].sum() != 0:
        non_zero_variables.append(missing_var)

# Remove from missing_frac_inen_energy the variables with non zero values
for non_zero in non_zero_variables:
    missing_frac_inen_energy.remove(non_zero)

# Build historical and projected data

historical_to_save_path = os.path.abspath(os.path.join(dir_path, "..", "input_to_sisepuede", "historical"))
projected_to_save_path = os.path.abspath(os.path.join(dir_path, "..", "input_to_sisepuede", "projected"))

var_to_save = sys.argv[1]

if var_to_save in missing_frac_inen_energy:
    historical_template[var_to_save] = 0.0
    projected_template[var_to_save] = 0.0

    historical_file_path = os.path.join(historical_to_save_path, f"{var_to_save}.csv")
    projected_file_path = os.path.join(projected_to_save_path, f"{var_to_save}.csv")

    historical_template.to_csv(historical_file_path, index = False)
    projected_template.to_csv(projected_file_path, index = False)

'''
non_zero_variable = non_zero_variables[0]

## Get all variables of the group
prefix_group = "frac_inen_energy_agriculture_and_livestock"
all_var_prefix_group = [f for f in all_frac_inen_energy if prefix_group in f]

## Load all variables from sisepuede_data repository

historical_template = pd.read_csv("https://raw.githubusercontent.com/milocortes/sisepuede_data/main/Energy/frac_inen_energy_cement_natural_gas/input_to_sisepuede/historical/frac_inen_energy_cement_natural_gas.csv")      
projected_template = pd.read_csv("https://raw.githubusercontent.com/milocortes/sisepuede_data/main/Energy/frac_inen_energy_cement_natural_gas/input_to_sisepuede/projected/frac_inen_energy_cement_natural_gas.csv")      

historical_template = historical_template[["Nation","iso_code3", "Year"]]                                                                                                                                                                    
projected_template = projected_template[["Nation","iso_code3", "Year"]]                                                                                                                                                                    


all_group_historical = historical_template.copy()
all_group_projected = projected_template.copy()

path_sisepuede_historical = lambda var_name : f"https://raw.githubusercontent.com/milocortes/sisepuede_data/main/Energy/{var_name}/input_to_sisepuede/historical/{var_name}.csv"
path_sisepuede_projected = lambda var_name : f"https://raw.githubusercontent.com/milocortes/sisepuede_data/main/Energy/{var_name}/input_to_sisepuede/projected/{var_name}.csv"

for var_group in all_var_prefix_group:
    if var_group != non_zero_variable or var_group != "frac_inen_energy_agriculture_and_livestock_hydrogen" or var_group != "frac_inen_energy_agriculture_and_livestock_gas_petroleum_liquid": 
        print(var_group)
        historical_group_var = pd.read_csv(path_sisepuede_historical(var_group))
        projected_group_var = pd.read_csv(path_sisepuede_projected(var_group))

        all_group_historical[var_group] = historical_group_var[var_group]
        all_group_projected[var_group] = projected_group_var[var_group]


'''