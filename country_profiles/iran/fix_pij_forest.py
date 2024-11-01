import pandas as pd 

df = pd.read_csv("real_data.csv")

### NO hay transiciones de forest primary a cualquier otro estado

forests_primary_to_cualquiera = ['pij_lndu_forests_primary_to_grasslands',
 'pij_lndu_forests_primary_to_forests_mangroves',
 'pij_lndu_forests_primary_to_croplands',
 'pij_lndu_forests_primary_to_settlements',
 'pij_lndu_forests_primary_to_forests_secondary',
 'pij_lndu_forests_primary_to_other',
 'pij_lndu_forests_primary_to_wetlands']

df[forests_primary_to_cualquiera] = 0.0
df['pij_lndu_forests_primary_to_forests_primary'] = 1.0



# Cancela transiciones de forest primary a otros sectores
lndu_name = "forests_mangroves"

### Cancelamos las transiciones a  forest primary. Se lo agregamos a su propia transición
lndu_cats = [
    "other", "forests_primary", "croplands","grasslands", "forests_secondary", "forests_primary", "settlements"
]

for lndu in lndu_cats:
    pij_to_other_lndu = f'pij_lndu_{lndu}_to_{lndu_name}'
    pij_to_same = f'pij_lndu_{lndu}_to_{lndu}'

    df[pij_to_same] += df[pij_to_other_lndu]
    df[pij_to_other_lndu] = 0

### Incrementamos la transición de mangroves a other
param_to_share = 0.99

df['pij_lndu_forests_mangroves_to_other'] += 0.8864829999999999
df["pij_lndu_forests_mangroves_to_forests_mangroves"] -= 0.8864829999999999


df.to_csv("real_data.csv")