from assumption import historical_assumption, projected_assumption
import os 
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()


save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 


# Load ISO3 code
iso3_m49_correspondence = pd.read_html("https://unstats.un.org/unsd/methodology/m49/")[0]

iso3_m49_correspondence.rename(columns = {"Country or Area" : "Nation", "ISO-alpha3 code" : "iso_code3"}, inplace = True)
iso3_m49_correspondence = iso3_m49_correspondence[["Nation", "iso_code3"]]

## Convert LGE/100km  unit to sisepuede unit km/l [ km/l = ((LGE/100km)^-1)(1/100)  ]

for k,v in historical_assumption.items():
    historical_assumption[k] = (v**-1)*100

for k,v in projected_assumption.items():
    projected_assumption[k] = (v**-1)*100


var_energy_to_process = sys.argv[1]

time = range(2000, 2015)
df_var_energy = pd.DataFrame({"Year" : time, var_energy_to_process : [historical_assumption[var_energy_to_process]]*len(time)})

historical_df_var_energy = iso3_m49_correspondence.merge(right = df_var_energy, how = "cross") 

save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 

file_save_path_historical = os.path.join(save_path_historical, f"{var_energy_to_process}.csv")
historical_df_var_energy.to_csv(file_save_path_historical, index = False)

# Build and save to csv projected data
last_year = df_var_energy["Year"].to_list()[-1]

time_period = range(last_year +1, 2051)

# Interpolate data from 2014 (current technology) to 2050 (mature technology)
#x = [2015, 2050]
#y = [historical_assumption[var_energy_to_process], projected_assumption[var_energy_to_process]] 

#y_interpol = np.interp(range(last_year +2, 2050), x, y)

#y_all = [historical_assumption[var_energy_to_process]] + list(y_interpol) + [projected_assumption[var_energy_to_process]]

x = [2015, 2035, 2050] 
y = [historical_assumption[var_energy_to_process], 
     1.1*(historical_assumption[var_energy_to_process]),
     projected_assumption[var_energy_to_process]]

f = CubicSpline(x, y, bc_type='natural') 
x_new = np.linspace(last_year, 2050, 36) 
y_new = f(x_new)                                                                                                                                                                                          

projected_df_var_energy = pd.DataFrame({"Year" : time_period, var_energy_to_process : y_new})

all_projected_df_var_energy = iso3_m49_correspondence.merge( right = projected_df_var_energy, how = "cross")


save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

file_save_path_projected = os.path.join(save_path_projected, f"{var_energy_to_process}.csv")

all_projected_df_var_energy.to_csv(file_save_path_projected, index = False)
