import pandas as pd 

df = pd.read_csv("real_data.csv")

#### FIX INITIAL PROPORTIONS OF LNDU

other_pij = [i for i in df.columns if "pij_lndu_other_to" in i ]
other_pij.remove('pij_lndu_other_to_other')

df['pij_lndu_other_to_other'] = 1.0

df[other_pij] = 0.0

# Change to other
state = "other"
pij_to_other = [i for i in df.columns if i.endswith("to_other") ]
pij_to_other.remove(f"pij_lndu_{state}_to_{state}")

for state_to in pij_to_other:
    i_to_i = state_to.replace(f"_to_{state}","").replace("pij_lndu_","")
    i_to_i = f"pij_lndu_{i_to_i}_to_{i_to_i}"

    df[i_to_i] += df[state_to]
    df[state_to] = 0

###########################
# Change to wetlands

state = "wetlands"
pij_to_wetlands = [i for i in df.columns if i.endswith("to_wetlands") ]
pij_to_wetlands.remove(f"pij_lndu_{state}_to_{state}")

param_to = 1.0

for state_to in pij_to_wetlands:
    i_to_i = state_to.replace(f"_to_{state}","").replace("pij_lndu_","")
    i_to_i = f"pij_lndu_{i_to_i}_to_{i_to_i}"

    df[i_to_i] += param_to * df[state_to] 
    df[state_to] = (1-param_to) * df[state_to]

df.to_csv("real_data.csv")


 