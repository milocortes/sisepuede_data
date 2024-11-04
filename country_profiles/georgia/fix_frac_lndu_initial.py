import pandas as pd 
import numpy as np 

df = pd.read_csv("backup_real_data/real_data.csv")


#### FIX INITIAL PROPORTIONS OF LNDU

### FACT : Georgia also draws attention to the fact that 43.5% of the country’s territory is covered by forests
lndu_initial_frac_forest = 0.435
forest_fields = ["frac_lndu_initial_forests_secondary", "frac_lndu_initial_forests_primary", 'frac_lndu_initial_forests_mangroves']
df[forest_fields] = (df[forest_fields]/df[forest_fields].sum(axis = 1).to_numpy()[:,np.newaxis])*lndu_initial_frac_forest


lndu_initial_frac_no_forest = [
 'frac_lndu_initial_wetlands',
 'frac_lndu_initial_croplands',
 'frac_lndu_initial_other',
 'frac_lndu_initial_grasslands',
 'frac_lndu_initial_settlements']

df[lndu_initial_frac_no_forest] = (df[lndu_initial_frac_no_forest]/df[lndu_initial_frac_no_forest].sum(axis = 1).to_numpy()[:,np.newaxis])*(1-lndu_initial_frac_forest)

df[forest_fields + lndu_initial_frac_no_forest]

df.to_csv("real_data.csv", index = False)
