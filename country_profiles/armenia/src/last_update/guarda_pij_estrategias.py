import pandas as pd
import numpy as np
import subprocess
import os
import sys


DATA_PATH = "/opt/sisepuede/ref/ingestion/calibrated/armenia"
TZA_DATA = os.path.join(DATA_PATH, "model_input_variables_armenia_af_calibrated_backup.xlsx")
TZA_DATA_MODIF = os.path.join(DATA_PATH, "model_input_variables_armenia_af_calibrated.xlsx")

estrategias_backup = {i : pd.read_excel(TZA_DATA, sheet_name=f"strategy_id-{i}") for i in [0, 1015,5009]}
estrategias_modif = {i : pd.read_excel(TZA_DATA_MODIF, sheet_name=f"strategy_id-{i}") for i in [0, 1015,5009]}

