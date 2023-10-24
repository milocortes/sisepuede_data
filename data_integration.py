import pandas as pd
from tqdm import tqdm
import glob
from datetime import datetime

sisepuede_sector = ["AFOLU", "CircularEconomy", "IPPU", "SocioEconomic", "Energy"]

var_to_index = ["iso_code3", "Year"]

countries = ["ARG", "BHS", "BRB", "BMU", "BOL", "BRA", "CHL", "CHN", "COL", "CRI", "DOM", "ECU", "SLV", "GTM", "GUY",
             "HTI", "HND", "IND", "JPN", "MEX", "PAN", "PRY", "PER", "RUS", "SUR", "TUR", "URY", "VEN"]

country = "IND"
countries = ["IND"]

acumula_countries = []

for idx, country in enumerate(countries):
    print(f"#{idx} - {country}")
    acumula_files = []
    for sector in sisepuede_sector:

        historical_subsector_files = [i for i in glob.glob(f"{sector}/*/*/*/*.csv") if "historical"  in i] 
        projected_subsector_files = [i for i in glob.glob(f"{sector}/*/*/*/*.csv") if "projected"  in i]

        print(sector)
        for historical_file, projected_file in tqdm(zip(historical_subsector_files, projected_subsector_files)):

            historical_df = pd.read_csv(historical_file)
            projected_df = pd.read_csv(projected_file)

            historical_df = historical_df.rename(columns = {"location_code" : "iso_code3", "ISO3":"iso_code3", "year" : "Year"})
            projected_df = projected_df.rename(columns = {"location_code" : "iso_code3", "ISO3":"iso_code3", "year" : "Year"})

            historical_df = historical_df.query(f"iso_code3=='{country}'").reset_index(drop=True)
            projected_df = projected_df.query(f"iso_code3=='{country}'").reset_index(drop=True)

            historical_df["Year"] = historical_df["Year"].astype(int)
            projected_df["Year"] = projected_df["Year"].astype(int)

            sisepuede_var_name = [i for i in historical_df.columns if len(i.split("_")) > 2][0] 

            merge_df_sisepuede = pd.concat([historical_df[["iso_code3","Year",sisepuede_var_name]], projected_df[["iso_code3","Year",sisepuede_var_name]]])

            merge_df_sisepuede = merge_df_sisepuede.sort_values(["iso_code3", "Year"])

            merge_df_sisepuede = merge_df_sisepuede.set_index(var_to_index)

            merge_df_sisepuede = merge_df_sisepuede.loc[~merge_df_sisepuede.index.duplicated(keep='first')]

            merge_df_sisepuede = merge_df_sisepuede.query("Year >=2015 and Year<=2050")
            acumula_files.append(merge_df_sisepuede)

    real_data = pd.concat(acumula_files, axis = 1).reset_index()

    ### batch_data_generation
    #ippu_files = ["https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/batch_data_generation/ippu_cement_clinker_fraction/clinker_fraction_cement_ippu.csv", 
    #              "https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/batch_data_generation/ippu_cement_clinker_fraction/net_imports_cement_clinker.csv", 
    #              "https://github.com/egobiernoytp/lac_decarbonization/raw/main/ref/batch_data_generation/ippu_emission_factors_fcs/emission_factors_ippu_fcs.csv"]

    #join_ippu_data = pd.concat([pd.read_csv(f).query(f"iso_code3=='{country}' and year >= 2015").set_index(["iso_code3", "year"]) for f in ippu_files], axis = 1).reset_index(drop=True)

    #join_ippu_data.rename(columns = {"year":"Year"}, inplace = True)

    #real_data = pd.concat([real_data, join_ippu_data], axis = 1)

    fake_data_complete = pd.read_csv("https://raw.githubusercontent.com/jcsyme/sisepuede/main/ref/fake_data/fake_data_complete.csv")
    fake_data_complete = fake_data_complete[list(set(fake_data_complete.columns) - set(real_data.columns)) ]

    mix_data = pd.concat([real_data, fake_data_complete], axis = 1)

    acumula_countries.append(mix_data)

all_mix_data = pd.concat(acumula_countries, ignore_index = True)

today_date = str( datetime.now())[:10].replace("-","")

all_mix_data.to_csv(f"real_data_{today_date}.csv", index = False)