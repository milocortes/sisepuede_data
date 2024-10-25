import pandas as pd 

df = pd.read_csv("real_data.csv")
frac_inen = pd.read_csv("frac_inen_updated.csv")

df[frac_inen.columns] = frac_inen

df.to_csv("frac_inen_updated.csv", index = False)