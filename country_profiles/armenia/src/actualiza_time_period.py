import pandas as pd
import sys

time_period = int(sys.argv[1])

df = pd.DataFrame([(0+i, 2015+i) for i in range(time_period)], columns = ["time_period", "year"])

df.to_csv("/opt/sisepuede/docs/source/csvs/attribute_dim_time_period.csv", index = False)

