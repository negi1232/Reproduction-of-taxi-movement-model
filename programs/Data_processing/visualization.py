import os
import osmnx as ox
import json
import pickle
import sqlite3

ox.config(use_cache=True, log_console=False)

class Expert():
    def __init__(self,file_path) -> None:
        with open(file_path, 'rb') as web:
            self.G = pickle.load(web)
    def expart_data(trajectories):
        pass

        pass




    def import_data(self):
        con = sqlite3.connect("data.db")

        c = con.cursor()

        c.execute("select * from reshape_route")

        list1 = c.fetchone()
        print(list1)

def load_setting():#jsonファイルを読み込む
    with open('settings.json') as f:
        return json.load(f)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    setting=load_setting()#jsonファイルを読み込む
    print(str(setting["route_correction"]["osm_area"]))
    expert=Expert(setting["route_correction"]["osm_area"])
    expert.import_data()

    pass

