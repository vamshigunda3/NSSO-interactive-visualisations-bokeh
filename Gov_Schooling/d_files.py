import pandas as pd
from time import sleep
#import 
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global three_rounds, states
    three_rounds=pd.read_feather("./data/three_rounds.feather")
    print(three_rounds.head())
    three_rounds.dropna(inplace = True)
    three_rounds.reset_index(drop=True, inplace =True)
    states = pd.read_feather("./data/state_names.feather")
    all_data["data"] = three_rounds, states
    sleep(1.0/12)
