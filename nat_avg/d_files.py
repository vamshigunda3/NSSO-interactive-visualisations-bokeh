import pandas as pd
from time import sleep
#import 
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global df
    df = pd.read_feather("./data/national_avg.feather")
    all_data["data"] = df
    sleep(1.0/12)
