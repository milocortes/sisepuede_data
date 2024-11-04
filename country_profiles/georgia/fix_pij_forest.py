import pandas as pd 

df = pd.read_csv("real_data.csv")

# Cancela transiciones de forest primary a otros sectores
lndu_name = "wetlands"

"""
lndu_to_isolate = f"pij_lndu_{lndu_name}_to"
cancel_from_pij_to_all = [i for i in df.columns if lndu_to_isolate  in i ]
cancel_from_pij_to_all.remove(f"pij_lndu_{lndu_name}_to_{lndu_name}")
df[f"pij_lndu_{lndu_name}_to_{lndu_name}"] = 1.0

df[cancel_from_pij_to_all] = 0.0

"""

### Cancelamos las transiciones a  forest primary. Se lo agregamos a su propia transición
lndu_cats = [
    "other", "forests_mangroves", "croplands","grasslands", "forests_secondary", "forests_primary", "settlements"
]

for lndu in lndu_cats:
    pij_to_other_lndu = f'pij_lndu_{lndu}_to_{lndu_name}'
    pij_to_same = f'pij_lndu_{lndu}_to_{lndu}'

    df[pij_to_same] += df[pij_to_other_lndu]
    df[pij_to_other_lndu] = 0


# Cancela transiciones de forest primary a otros sectores
lndu_name = "forests_secondary"
"""
lndu_to_isolate = f"pij_lndu_{lndu_name}_to"
cancel_from_pij_to_all = [i for i in df.columns if lndu_to_isolate  in i ]
cancel_from_pij_to_all.remove(f"pij_lndu_{lndu_name}_to_{lndu_name}")
df[f"pij_lndu_{lndu_name}_to_{lndu_name}"] = 1.0

df[cancel_from_pij_to_all] = 0.0
"""
### Cancelamos las transiciones a  forest primary. Se lo agregamos a su propia transición
lndu_cats = [
    "other", "forests_mangroves", "croplands","grasslands", "forests_primary", "wetlands", "settlements"
]

for lndu in lndu_cats:
    pij_to_other_lndu = f'pij_lndu_{lndu}_to_{lndu_name}'
    pij_to_same = f'pij_lndu_{lndu}_to_{lndu}'

    df[pij_to_same] += df[pij_to_other_lndu]
    df[pij_to_other_lndu] = 0


### Incrementamos la transición de other a forest_secondary
param_to_share = 0.99

df['pij_lndu_wetlands_to_other'] += (1-param_to_share)*df['pij_lndu_wetlands_to_wetlands']
df['pij_lndu_wetlands_to_wetlands'] = param_to_share*df['pij_lndu_wetlands_to_wetlands']


df.to_csv("real_data.csv")