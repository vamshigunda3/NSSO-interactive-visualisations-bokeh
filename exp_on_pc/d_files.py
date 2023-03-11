import pandas as pd
import geopandas as gpd
from time import sleep
#import 
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global Final, s_shp, d_shp,state_n,district_n
    Final = pd.read_feather("./data/exp_on_pc.feather")
    s_shp = gpd.read_feather("./geo_feather/states.feather")
    d_shp = gpd.read_feather("./geo_feather/districts.feather")
    state_n = pd.read_feather("./data/state_names.feather")
    
    district_n = pd.read_feather("./data/district_names.feather")
    print(district_n.head())
    d_shp.rename(columns ={"dist_code":"district_code","dist_name":"district_name"},inplace = True)
    s_shp.state_code = s_shp.state_code.astype(int)
    d_shp.district_code = d_shp.district_code.astype(int)
    all_data["data"] = Final,s_shp,d_shp,state_n,district_n
    sleep(1.0/12)
        
