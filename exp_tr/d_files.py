import pandas as pd
from time import sleep
all_data = {"data":None}
print("you came to d_files")
def update_data():
    global data, s_shp, d_shp
    data = pd.read_feather("./data/exp_3rounds.feather")
   # df_col = ColumnDataSource(df)
    all_data["data"] = data
    sleep(1.0/12)
