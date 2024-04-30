import pandas as pd

df_input = pd.read_csv("MODEL_INPUT.csv")
df_output = pd.read_csv("MODEL_OUTPUT.csv")
df_complete = pd.concat([df_input, df_output[df_output.columns[3:]]], axis =1)
df_complete.to_csv("sisepuede_results_sisepuede_run_ssp.csv", index = False)
