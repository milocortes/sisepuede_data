import pandas as pd 
import matplotlib.pyplot as plt 
import os

from grupos_subsectores_emisiones import componen_emisiones_subsector

#contenedor = "tanzania_pij_uno"
#PATH_INPUT = f"/home/milo/Documents/egap/SISEPUEDE/{contenedor}/ssp_tanzania/opt/SSP_RESULTS"
#PATH_INPUT = "/home/milo/Documents/egap/BancoMundial/paises/armenia/ssp_model/opt/SSP_RESULTS"
#PATH_INPUT = "/home/milo/Documents/egap/BancoMundial/paises/armenia/5009_light/salidas"
#PATH_INPUT = "/home/milo/Documents/egap/BancoMundial/paises/india/ssp_india/opt/SSP_RESULTS"
PATH_INPUT = "/home/milo/Documents/egtp/SISEPUEDE/sisepuede_data/country_profiles/iran/ssp_iran/opt/SSP_RESULTS"
#PATH_INPUT = "/home/milo/Documents/egap/BancoMundial/paises/iran/ssp_iran/opt/SSP_RESULTS"


#DATA_PATH = os.path.join(PATH_INPUT,"sisepuede_results_sisepuede_run_ssp.csv")
DATA_PATH = os.path.join(PATH_INPUT,"MODEL_OUTPUT.csv")


strategy_mapping = {
    0: [0,'Baseline NDP'],
   15015: [1015,'LNDU: Partial land use reallocation'],
   126126: [5007,'PFLO: All transformations without stopping deforestation and partial land use reallocation'],
   125125: [5006,'PFLO: Supply side technologies and transformations'],
   127127: [5008,'PFLO: All transformations'], 
   128128: [5009,'PFLO: All transformations with partial land use reallocation'],
   14014: [1014, "LNDU: Expand sustainable grazing practices"], 
   119119: [4008, "IP: All IP transformations"], 
   120120: [5001, "PFLO: Better baseline"], 
   123123: [5004, "PFLO: Change consumer behavior"], 
   124124: [5005, "PFLO: Industrial point of capture CCSQ"]
}


df = pd.read_csv(DATA_PATH)

to_lndu = "forest_primary"

conversion_to_primary_secondary = [i for i in df.columns if i.endswith(to_lndu) and i.startswith("area_lndu_conversion_from_") and "_to_" in i]

from_forests_secondary_to_states =  [i for i in df.columns if "area_lndu_conversion_from_forests_secondary_to" in i]

from_forests_primary_to_states =  [i for i in df.columns if "area_lndu_conversion_from_forests_primary_to" in i]

areas = [ 'area_lndu_croplands',
 'area_lndu_forests_mangroves',
 'area_lndu_forests_primary',
 'area_lndu_forests_secondary',
 'area_lndu_grasslands',
 'area_lndu_other',
 'area_lndu_settlements',
 'area_lndu_wetlands']

data_TIMES = [('area_lndu_croplands', 26.0, 28.0),
                ('area_lndu_forests_mangroves', 0.0, 0.0),
                ('area_lndu_forests_primary', 11.0, 14.0),
                ('area_lndu_forests_secondary', 9.0, 19.0),
                ('area_lndu_grasslands', 43.0, 29.0),
                ('area_lndu_other', 3.0, 3.0),
                ('area_lndu_settlements', 4.0, 4.0),
                ('area_lndu_wetlands', 4.0, 4.0)]

emisiones_subsector = [i for i in df.columns if i.startswith("emission_co2e_subsector_total_")]

df_data_TIMES = pd.DataFrame(data_TIMES, columns = ["ssp_var", "2015_TIMES", "2050_TIMES"]).set_index("ssp_var")

guarda_emisiones_totales = {}
subsectores_lista = ['agrc','ccsq','entc','fgtv','frst','inen','ippu','lndu','lsmm','lvst','scoe','trns','trww','waso']
guarda_emisiones = {i : pd.DataFrame() for i in subsectores_lista}


for estrategia in df.primary_id.unique():
    df_lndu_strategy = df.query(f"primary_id=={estrategia}")[["time_period"]+areas]
    all_lndu_Area = df_lndu_strategy.sum(axis=1).to_numpy()
    df_lndu_strategy.reset_index(drop=True)
    df_lndu_strategy = df_lndu_strategy.reset_index(drop=True)
    df_lndu_strategy["time_period"] = df_lndu_strategy["time_period"] + 2015
    df_lndu_strategy = df_lndu_strategy.set_index("time_period")
    df_lndu_strategy.div(all_lndu_Area, axis = 0).plot.area(title = f"Estrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()
    #df_lndu_strategy["area_lndu_forests"] = df_lndu_strategy["area_lndu_forests_primary"] + df_lndu_strategy["area_lndu_forests_secondary"] + df_lndu_strategy["area_lndu_forests_mangroves"]

    """
    print(f"\n\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    cols_porcentaje = ['area_lndu_croplands', 'area_lndu_forests_primary', 'area_lndu_forests_secondary', 'area_lndu_grasslands','area_lndu_other','area_lndu_settlements','area_lndu_wetlands']
    print(df_lndu_strategy.loc[[2015,2050], cols_porcentaje].pct_change()*100)

    print("\nRAZONES\n")
    simulacion_ssp = (df_lndu_strategy.div(all_lndu_Area, axis = 0).loc[[2015,2020,2070]].T*100).round()
    simulacion_ssp.columns = ["2015_SSP", "2020_SSP", "2070_SSP"]

    #simulacion_times = pd.DataFrame({""})
    #print(pd.concat([df_data_TIMES,simulacion_ssp], axis = 1))
    #print(pd.concat([simulacion_ssp], axis = 1))
    print(simulacion_ssp[["2015_SSP", "2070_SSP"]])
    """
    ### Ploteamos cuanda lndu se va a forest primary
    """
    df_lndu_strategy = df.query(f"primary_id=={estrategia}")[["time_period"]+conversion_to_primary_secondary]
    all_lndu_Area = df_lndu_strategy.sum(axis=1).to_numpy()
    df_lndu_strategy.reset_index(drop=True)
    df_lndu_strategy = df_lndu_strategy.reset_index(drop=True)
    df_lndu_strategy["time_period"] = df_lndu_strategy["time_period"] + 2015
    df_lndu_strategy = df_lndu_strategy.set_index("time_period")
    df_lndu_strategy.div(all_lndu_Area, axis = 0).plot.area(title = f"Estrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()
    """

    ########### EMISIONES TOTALES
    df_emisiones_strategy = df.query(f"primary_id=={estrategia}")[["time_period"]+emisiones_subsector]
    df_emisiones_strategy.reset_index(drop=True)
    df_emisiones_strategy = df_emisiones_strategy.reset_index(drop=True)
    df_emisiones_strategy["time_period"] = df_emisiones_strategy["time_period"] + 2015
    df_emisiones_strategy = df_emisiones_strategy.set_index("time_period").drop(columns = ["emission_co2e_subsector_total_soil"])
    df_emisiones_strategy.plot.area(title = f"EMISIONES\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()

    for i in subsectores_lista:
        query_subsector = [k for k in df_emisiones_strategy.columns if i in k]
        guarda_emisiones[i] = pd.concat([guarda_emisiones[i], df_emisiones_strategy[query_subsector]], axis = 1)
        guarda_emisiones[i] = guarda_emisiones[i].rename(columns = {query_subsector[0] : f"{query_subsector[0]}_{strategy_mapping[estrategia][1]}"})


    """
    for sub_sector in df_emisiones_strategy.columns:

        df_sub_emisiones_strategy = df.query(f"primary_id=={estrategia}")[["time_period"]+componen_emisiones_subsector[sub_sector]]
        df_sub_emisiones_strategy.reset_index(drop=True)
        df_sub_emisiones_strategy = df_sub_emisiones_strategy.reset_index(drop=True)
        df_sub_emisiones_strategy["time_period"] = df_sub_emisiones_strategy["time_period"] + 2015
        df_sub_emisiones_strategy = df_sub_emisiones_strategy.set_index("time_period")
        try:
            df_sub_emisiones_strategy.plot.area(title = f"EMISIONES\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}\nSUBSECTOR : {sub_sector}")
            plt.show()    
        except:
            print("NO jalo")

    """

    """
    ########### AREA LNDU CONVERSION FROM FOREST SECONDARY
    df_conversion_from_forest_sec = df.query(f"primary_id=={estrategia}")[["time_period"]+["area_lndu_conversion_from_forests_secondary"]]
    df_conversion_from_forest_sec.reset_index(drop=True)
    df_conversion_from_forest_sec = df_conversion_from_forest_sec.reset_index(drop=True)
    df_conversion_from_forest_sec["time_period"] = df_conversion_from_forest_sec["time_period"] + 2015
    df_conversion_from_forest_sec = df_conversion_from_forest_sec.set_index("time_period")
    df_conversion_from_forest_sec.plot.area(title = f"AREA LNDU CONVERSION FROM FOREST SECONDARY\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()

    ########### AREA LNDU CONVERSION FROM FOREST PRIMARY to other state
    df_conversion_from_forest_primary_to_states = df.query(f"primary_id=={estrategia}")[["time_period"]+from_forests_primary_to_states]
    df_conversion_from_forest_primary_to_states.reset_index(drop=True)
    df_conversion_from_forest_primary_to_states = df_conversion_from_forest_primary_to_states.reset_index(drop=True)
    df_conversion_from_forest_primary_to_states["time_period"] = df_conversion_from_forest_primary_to_states["time_period"] + 2015
    df_conversion_from_forest_primary_to_states = df_conversion_from_forest_primary_to_states.set_index("time_period")
    df_conversion_from_forest_primary_to_states.plot.area(title = f"AREA LNDU CONVERSION FROM FOREST PRIMARY TO STATES\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()

    ########### AREA LNDU CONVERSION FROM FOREST SECONDARY to other state
    df_conversion_from_forest_sec_to_states = df.query(f"primary_id=={estrategia}")[["time_period"]+from_forests_secondary_to_states]
    df_conversion_from_forest_sec_to_states.reset_index(drop=True)
    df_conversion_from_forest_sec_to_states = df_conversion_from_forest_sec_to_states.reset_index(drop=True)
    df_conversion_from_forest_sec_to_states["time_period"] = df_conversion_from_forest_sec_to_states["time_period"] + 2015
    df_conversion_from_forest_sec_to_states = df_conversion_from_forest_sec_to_states.set_index("time_period")
    df_conversion_from_forest_sec_to_states.plot.area(title = f"AREA LNDU CONVERSION FROM FOREST SECONDARY TO STATES\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()

    ########### AREA LNDU CONVERSION FROM FOREST PRIMARY TO CROPLANDS
    df_conversion_from_forest_sec = df.query(f"primary_id=={estrategia}")[["time_period"]+["area_lndu_conversion_from_forests_primary"]]
    df_conversion_from_forest_sec.reset_index(drop=True)
    df_conversion_from_forest_sec = df_conversion_from_forest_sec.reset_index(drop=True)
    df_conversion_from_forest_sec["time_period"] = df_conversion_from_forest_sec["time_period"] + 2015
    df_conversion_from_forest_sec = df_conversion_from_forest_sec.set_index("time_period")
    df_conversion_from_forest_sec.plot.area(title = f"AREA LNDU CONVERSION FROM FOREST PRIMARY TO CROPLANDS\nEstrategia : {strategy_mapping[estrategia][1]}\nCODE:{strategy_mapping[estrategia][0]}")
    plt.show()
    """

    guarda_emisiones_totales[estrategia] = df_emisiones_strategy.sum(axis = 1).to_list()


for k,v in guarda_emisiones_totales.items():
    plt.plot(range(2015, 2051), v, label = f"EMISIONES\nEstrategia : {strategy_mapping[k][1]}")

plt.title("Emisiones estretgias")
plt.legend()
plt.show()


for k,v in guarda_emisiones.items():
    v.plot()
    plt.show()


    