import pandas as pd
import numpy as np
import subprocess
import os
import sys


DATA_PATH = "/opt/sisepuede/ref/ingestion/calibrated/armenia"
TZA_DATA = os.path.join(DATA_PATH, "model_input_variables_armenia_af_calibrated_backup.xlsx")
TZA_DATA_MODIF = os.path.join(DATA_PATH, "model_input_variables_armenia_af_calibrated.xlsx")

estrategias = {i : pd.read_excel(TZA_DATA, sheet_name=f"strategy_id-{i}") for i in [0, 1015,5009]}

# Copy file from backup
subprocess.run(["cp", TZA_DATA , TZA_DATA_MODIF])

# Save changes
writer = pd.ExcelWriter(TZA_DATA_MODIF, engine='openpyxl', mode='a')
workBook = writer.book

for estrategia_id, datos_estrategias in estrategias.items():
    pij_all = list(datos_estrategias[[True if "pij" in i else False for i in datos_estrategias.variable]].variable)

    pij_diagonal = ['pij_lndu_croplands_to_croplands',
                    'pij_lndu_forests_mangroves_to_forests_mangroves',
                    'pij_lndu_forests_primary_to_forests_primary',
                    'pij_lndu_forests_secondary_to_forests_secondary',
                    'pij_lndu_grasslands_to_grasslands',
                    'pij_lndu_other_to_other',
                    'pij_lndu_settlements_to_settlements',
                    'pij_lndu_wetlands_to_wetlands']

    states = ['pij_lndu_croplands',
            'pij_lndu_forests_mangroves',
            'pij_lndu_forests_primary',
            'pij_lndu_forests_secondary',
            'pij_lndu_grasslands',
            'pij_lndu_other',
            'pij_lndu_settlements',
            'pij_lndu_wetlands']

    states = list(np.array(states)[[any([j.startswith(i) for j in pij_all]) for i in states]])

    pij_to_stress = (set(pij_all) - set(pij_diagonal))


    if pij_to_stress:
        states_groups = {state : [i for i in pij_all if i.startswith(state) and not i in pij_diagonal] for state in states}

        scale_max = 1.2
        scale_min = 0.8

        states_factors = {state : {i:j for i,j in
                                        zip(
                                            states_groups[state]
                                            ,
                                            scale_max - scale_min*np.random.rand(len(states_groups[state]))
                                        )

                                    }


                            for state in states}



        df_pij_to_stress = datos_estrategias.set_index("variable").loc[pij_all][range(36)].T
        df_pij_to_stress_compara = datos_estrategias.set_index("variable").loc[pij_all][range(36)].T

        guarda_grassland_to_grassland = df_pij_to_stress["pij_lndu_grasslands_to_forests_secondary"]


        if "pij_lndu_other_to_other" in list(df_pij_to_stress.columns):
            print(f"SISTA : ESTRATEGIA ID {estrategia_id}")
            states_factors["pij_lndu_other"].update({'pij_lndu_other_to_forests_primary': 1.5,
                                                'pij_lndu_other_to_grasslands': 2.0})

        for state in states:
            for state_group in states_groups[state]:
                df_pij_to_stress[state_group] *= states_factors[state][state_group]

        #df_pij_to_stress["pij_lndu_forests_secondary_to_forests_secondary"] *=0.9
        #df_pij_to_stress["pij_lndu_wetlands_to_wetlands"] *=0.99


        if "pij_lndu_other_to_other" in list(df_pij_to_stress.columns):
            print(f"SISTA : ESTRATEGIA ID {estrategia_id}")

            #df_pij_to_stress["pij_lndu_croplands_to_croplands"] *=1.0
            df_pij_to_stress["pij_lndu_other_to_other"] *=0.1



        if estrategia_id ==0:

            df_pij_to_stress['frac_lndu_initial_croplands'] = 0.26
            df_pij_to_stress['frac_lndu_initial_forests_mangroves'] = 0.00
            df_pij_to_stress['frac_lndu_initial_forests_primary'] = 0.11
            df_pij_to_stress['frac_lndu_initial_forests_secondary'] = 0.09
            df_pij_to_stress['frac_lndu_initial_grasslands'] = 0.43
            df_pij_to_stress['frac_lndu_initial_other'] = 0.03
            df_pij_to_stress['frac_lndu_initial_settlements'] = 0.04
            df_pij_to_stress['frac_lndu_initial_wetlands'] = 0.04


        #df_pij_to_stress["pij_lndu_grasslands_to_forests_secondary"] = 0.0


        for i,j in states_groups.items():
            pij_original_state = i+ "_to_" + "_".join(i.split("_")[2:])
            pij_all_group = j + [pij_original_state]

            #print("\nPre-Normalización\n")
            #print(df_pij_to_stress[pij_all_group].sum(axis = 1))

            normalization_vec = 1 - df_pij_to_stress[pij_original_state]
            df_pij_to_stress[j] = df_pij_to_stress[j].div(df_pij_to_stress[j].sum(axis = 1), axis = 0).multiply(normalization_vec, axis = 0)

            #print("\nPost-Normalizacion\n")
            #print(df_pij_to_stress[pij_all_group].sum(axis = 1))

        df_pij_to_stress = df_pij_to_stress.replace(np.nan, 0.0).T
        estrategias[estrategia_id] = datos_estrategias.set_index("variable")

        for i in df_pij_to_stress.index:
            estrategias[estrategia_id].loc[i, range(36)] = df_pij_to_stress.loc[i, range(36)]

        estrategias[estrategia_id] = estrategias[estrategia_id].reset_index()
        workBook.remove(workBook[f"strategy_id-{estrategia_id}"])
        estrategias[estrategia_id].to_excel(writer, sheet_name = f"strategy_id-{estrategia_id}", index = False)
writer.close()