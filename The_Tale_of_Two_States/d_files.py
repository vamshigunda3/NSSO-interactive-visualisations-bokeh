import pandas as pd
import geopandas as gpd
from time import sleep
#import 
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global df, s_shp, d_shp,state_n,district_n
    df = pd.read_feather("./data/TTSS.feather")
    s_shp = gpd.read_feather("./geo_feather/states.feather")
    d_shp = gpd.read_feather("./geo_feather/districts.feather")
    state_n = pd.read_feather("./data/state_names.feather")
    district_n = pd.read_feather("./data/district_names.feather")
    d_shp.rename(columns ={"dist_code":"district_code","dist_name":"district_name"},inplace = True)
    s_shp.state_code = s_shp.state_code.astype(int)
    d_shp.district_code = d_shp.district_code.astype(int)
    d_shp = d_shp[d_shp.state_name.isin(['UTTAR PRADESH','BIHAR'])]
    s_shp = s_shp[s_shp.state_name.isin(['UTTAR PRADESH','BIHAR'])]
    all_data["data"] = df,s_shp,d_shp,state_n,district_n
    sleep(1.0/12)
        
