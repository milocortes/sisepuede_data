import pandas as pd 
import os 
import sys


sisepuede_name = sys.argv[1]

# Set directories
dir_path = os.path.dirname(os.path.realpath(__file__))
#dir_path = os.getcwd()

sources_path = os.path.abspath(os.path.join(dir_path,"..","raw_data" ))
#save_path = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ))

# Load raw transition data
transitions_path = os.path.join(sources_path,"transition_probs_by_region_mean_with_target_growth-max_diagonal.csv")
transitions = pd.read_csv(transitions_path)

## Load M49 codes
#m49_countries = pd.read_json("https://data.apps.fao.org/catalog/dataset/1712bf04-a530-4d55-bb66-54949213985f/resource/b0c1d224-23ea-425d-b994-e15f76feb26b/download/m49-countries.json")
m49_countries = pd.read_json(os.path.join(sources_path, "m49-countries.json"))
m49_countries.m49 = m49_countries.m49.apply(lambda x : f"{x:03d}")

# functio to reformat the country name for integration
def format_country_name(country: str) -> str:
    country_out = country.split("(")[0].strip().lower().replace(" ", "_")
    return country_out

# Rename country names
m49_countries["country"] = m49_countries.country_name_en.apply(lambda x: format_country_name(x)) 


## Merge ISO3 codes
#transitions.m49 = transitions.m49.apply(lambda x : x.replace("'",""))
#transitions["iso_code3"] = transitions.m49.replace({i:j for i,j in zip(m49_countries["m49"], m49_countries["ISO3"])})
transitions["iso_code3"] = transitions["country"].replace({i:j for i,j in zip(m49_countries["country"], m49_countries["ISO3"])})
transitions = transitions[[True if len(i)==3 else False for i in transitions["iso_code3"]]]
transitions = transitions.drop(columns = "country")

transitions["Nation"] = transitions.iso_code3.replace({i:j for i,j in zip(m49_countries["ISO3"], m49_countries["country_name_en"])})

transitions = transitions.drop_duplicates(subset=['time_period','iso_code3','Nation'], keep='first') 

transitions = transitions.rename(columns = {"time_period":"Year"})

transitions["Year"] = transitions["Year"].replace( {i:j for i,j in zip(range(36), range(2015,2051))} )

transition = transitions.reset_index(drop = True) 


transition_pij = transition[["Year", "Nation", "iso_code3", sisepuede_name]]


### Save data
save_path_historical = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"historical" )) 
save_path_projected = os.path.abspath(os.path.join(dir_path,"..","input_to_sisepuede" ,"projected" )) 

## Save historical data
relative_path_to_save_historical_file = os.path.join(save_path_historical, f"{sisepuede_name}.csv")
transition_pij.query("Year<=2020").to_csv(relative_path_to_save_historical_file, index = False)

## Save projected data
relative_path_to_save_projected_file = os.path.join(save_path_projected, f"{sisepuede_name}.csv")
transition_pij.query("Year>2020").to_csv(relative_path_to_save_projected_file, index = False)
