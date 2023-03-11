import pandas as pd
import geopandas as gpd
from time import sleep
from bokeh.models import ColumnDataSource
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global df, s_shp, d_shp, state_n, district_n
    df = pd.read_feather("./data/medium_of_inst.feather")
    s_shp = gpd.read_feather("./geo_feather/states.feather")
    d_shp = gpd.read_feather("./geo_feather/districts.feather")
    d_shp.rename(columns = {"dist_code":"district_code","dist_name":"district_name"},inplace = True)
    state_n = pd.read_feather("./data/state_names.feather")
    district_n = pd.read_feather("./data/district_names.feather")
   # df_col = ColumnDataSource(df)
    all_data["data"] = df, s_shp, d_shp, state_n, district_n#, #df_col
    sleep(1.0/12)
