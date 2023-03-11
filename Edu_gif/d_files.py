import pandas as pd
import geopandas as gpd
from time import sleep
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    #global three_rounds, states_g, states_n
    three_rounds = pd.read_feather("./data/three_rounds.feather")
    states_n = pd.read_feather("./data/state_names.feather")
    states_g = gpd.read_feather("./geo_feather/states.feather")
    states_g.state_code = states_g.state_code.astype(int)
    three_rounds.dropna(inplace = True)
    three_rounds.reset_index(drop = True, inplace=True)
    all_data["data"] = three_rounds, states_g, states_n
    sleep(1.0/12)
        
