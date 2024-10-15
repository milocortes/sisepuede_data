import pandas as pd 

df = pd.read_csv("backup_real_data/real_data.csv")


#### FIX INITIAL PROPORTIONS OF LNDU

df['frac_lndu_initial_croplands'] = 0.435
df['frac_lndu_initial_forests_mangroves'] = 0.01
df['frac_lndu_initial_forests_primary'] = 0.135
df['frac_lndu_initial_forests_secondary'] = 0.09
df['frac_lndu_initial_grasslands'] = 0.01
df['frac_lndu_initial_other'] = 0.23
df['frac_lndu_initial_settlements'] = 0.015
df['frac_lndu_initial_wetlands'] = 0.075



croplands_pij = [i for i in df.columns if "pij_lndu_croplands_to" in i ]
croplands_pij.remove('pij_lndu_croplands_to_croplands')
df['pij_lndu_croplands_to_croplands'] = 1.0

df[croplands_pij] = 0.0

"""
df['pij_lndu_other_to_other'] = 1.0

df[other_pij] = 0.0

# Change to other
pij_to_other = [i for i in df.columns if i.endswith("to_other") ]

df["pij_lndu_grasslands_to_grasslands"]  += df['pij_lndu_grasslands_to_other']
df['pij_lndu_grasslands_to_other'] = 0.0

df["pij_lndu_settlements_to_settlements"] += df['pij_lndu_settlements_to_other']
df['pij_lndu_settlements_to_other'] = 0.0

df['pij_lndu_croplands_to_croplands'] += df['pij_lndu_croplands_to_other']
df['pij_lndu_croplands_to_other'] = 0.0

df['pij_lndu_wetlands_to_wetlands'] +=df['pij_lndu_wetlands_to_other']
df['pij_lndu_wetlands_to_other'] = 0.0


df['pij_lndu_forests_primary_to_forests_primary'] += df['pij_lndu_forests_primary_to_other']
df['pij_lndu_forests_primary_to_other'] = 0.0

df['pij_lndu_forests_mangroves_to_forests_mangroves'] += df['pij_lndu_forests_mangroves_to_other']
df['pij_lndu_forests_mangroves_to_other'] = 0.0


#### pij_lndu_forests_secondary_to_other ---> pij_lndu_forests_secondary_to_grassland
df['pij_lndu_forests_secondary_to_grasslands'] += df['pij_lndu_forests_secondary_to_other']
df['pij_lndu_forests_secondary_to_other'] = 0.0
"""

### Limitamos que grassland vaya a forest secondary

#param_to_share = 0.9

#df['pij_lndu_grasslands_to_grasslands'] += param_to_share*df['pij_lndu_grasslands_to_forests_secondary']

#df['pij_lndu_grasslands_to_forests_secondary'] = (1-param_to_share)*df['pij_lndu_grasslands_to_forests_secondary']

### Limitamos que grassland vaya a wetlands
#param_to_share = 1.0

#df['pij_lndu_grasslands_to_grasslands'] += param_to_share*df['pij_lndu_grasslands_to_wetlands']

#df['pij_lndu_grasslands_to_wetlands'] = (1-param_to_share)*df['pij_lndu_grasslands_to_wetlands']

#param_to_share = 0.8

#df['pij_lndu_grasslands_to_grasslands'] += param_to_share*df['pij_lndu_grasslands_to_wetlands']

#df['pij_lndu_grasslands_to_wetlands'] = (1-param_to_share)*df['pij_lndu_grasslands_to_wetlands']

#param_to_share = 0.9

#df['pij_lndu_wetlands_to_forests_secondary'] += param_to_share*df['pij_lndu_wetlands_to_wetlands']

#df['pij_lndu_wetlands_to_wetlands'] = (1-param_to_share)*df['pij_lndu_wetlands_to_wetlands']


### Incrementamos la transición de other a croplands y a settlements

#param_to_share = 0.95

#df['pij_lndu_other_to_croplands'] += (1-param_to_share)*df['pij_lndu_other_to_other']
#df['pij_lndu_other_to_other'] = param_to_share*df['pij_lndu_other_to_other']

#param_to_share = 0.9
#df['pij_lndu_other_to_settlements'] += (1-param_to_share)*df['pij_lndu_other_to_other']
#df['pij_lndu_other_to_other'] = param_to_share*df['pij_lndu_other_to_other']

### Incrementamos la transición de croplands a croplands al restarle a forest_secondary
#param_to_share = 0.3

#df['pij_lndu_croplands_to_croplands'] += (param_to_share)*df['pij_lndu_croplands_to_forests_secondary']
#df['pij_lndu_croplands_to_forests_secondary'] = (1-param_to_share)*df['pij_lndu_croplands_to_forests_secondary']

### Incrementamos la transición de forest_secondary a croplands al restarle a forest_secondary to forest_secondary
#param_to_share = 0.99

#df['pij_lndu_forests_secondary_to_croplands'] += (1-param_to_share)*df['pij_lndu_forests_secondary_to_forests_secondary']
#df['pij_lndu_forests_secondary_to_forests_secondary'] = param_to_share*df['pij_lndu_forests_secondary_to_forests_secondary']


### Cancelamos la transición others to croplands. Agregamos el peso a forest secondary
df['pij_lndu_other_to_forests_secondary'] += df['pij_lndu_other_to_croplands']
df['pij_lndu_other_to_croplands'] = 0

### Incrementamos la transición de other a forest_secondary
param_to_share = 0.985

df['pij_lndu_other_to_forests_secondary'] += (1-param_to_share)*df['pij_lndu_other_to_other']
df['pij_lndu_other_to_other'] = param_to_share*df['pij_lndu_other_to_other']


param_to_share = 0.99
df['pij_lndu_other_to_settlements'] += (1-param_to_share)*df['pij_lndu_other_to_other']
df['pij_lndu_other_to_other'] = param_to_share*df['pij_lndu_other_to_other']


df.to_csv("real_data.csv")