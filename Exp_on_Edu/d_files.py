import pandas as pd
from time import sleep
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global Exp 
    Exp=pd.read_feather("./data/exp_on_edu.feather")
    print(Exp.head())
    all_data["data"] = Exp
    sleep(1.0/12)
