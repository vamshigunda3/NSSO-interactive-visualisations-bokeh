import pandas as pd
from time import sleep

all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global Final
    Final = pd.read_feather("./data/he_tec.feather")
    all_data["data"] = Final
    sleep(1.0/12)
