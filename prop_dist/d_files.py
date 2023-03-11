import pandas as pd
from time import sleep
#import 
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global fv
    fv = pd.read_feather("./data/prop_dist.feather")
    all_data["data"] = fv
    sleep(1.0/12)
