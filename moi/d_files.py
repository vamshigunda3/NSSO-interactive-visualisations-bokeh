import pandas as pd
from time import sleep
all_data = {"data":None}
print("you came to d_files")
import os
print(os.getcwd())
def update_data():
    global iv
    iv=pd.read_feather("./data/language.feather")
    all_data["data"] = iv
    sleep(1.0/12)
