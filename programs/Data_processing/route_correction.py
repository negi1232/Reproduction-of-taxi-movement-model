import os
import numpy as np
import json
from tqdm import tqdm
import numpy as np
import osmnx as ox
import pickle
import sqlite3
ox.config(use_cache=True, log_console=False)
import rc_lib.data_pipe  as data_pipe

def load_setting():#jsonファイルを読み込む
    with open('../settings.json') as f:
        json_open = f
        return json.load(json_open)

def calc_area(routes):#演算を行う正方形のエリアを計算
    z=[routes[0],routes[0],routes[1],routes[1]]
    z0=list()
    z1=list()
    # ---z0----
    #|         |
    #z3        z2
    #|         |
    #----z1----
    for r in routes:
        z0.append(r[0])
        z1.append(r[1])
    z=[max(z0),min(z0),max(z1),min(z1)]
    if max(z0)-min(z0) >= max(z1)-min(z1):
        d= abs(max(z0)-min(z0))-(max(z1)-min(z1))
        z[2]+=d/2
        z[3]-=d/2
    else:
        d= abs(max(z0)-min(z0)),(max(z1)-min(z1))
        z[0]+=d/2
        z[1]-=d/2

    return z

class cal_route:
    def __init__(self,z,setting) :
        print("area="+str(z))

        save_path='./maps/'
        file_name='map_'+str(z)+'.binaryfile'
        
        if file_name in os.listdir(path='./maps/') :
            with open(save_path+file_name, 'rb') as web:
                self.G = pickle.load(web)
        else:
            self.G = ox.graph_from_bbox(z[0],z[1],z[2],z[3], network_type='drive')
        
            with open(save_path+file_name, 'wb') as web:
                pickle.dump(self.G , web)
       
        opts = {"node_size": 5, "bgcolor": "white", "node_color": "blue", "edge_color": "blue"}
        ox.plot_graph(self.G, show=False, save=True, filepath="road_network.png", **opts)
        
        
        #settingファイルにareaを記録
        with open('../settings.json') as f:
            json_open = f
            df= json.load(json_open)
        
        df["Data_processing"]["osm_area"]=str(z)
        with open('../settings.json', 'w') as f:
            json.dump(df, f,indent=4)

        #self.G = ox.graph_from_bbox(37.8780,37.4710,-122.1010 ,-122.5085, network_type='drive')
        self.fmap = ox.plot_graph_folium(self.G)
        self.last_pos=[0,0]
        self.route_dict={}
        self.point_dict={}
    
    def reset(self):
        self.last_pos=[0,0]

    def calc(self,lat,lon):
        if self.last_pos!=[0,0] and self.last_pos!=[lat,lon]:
            
            #もしすでに探索済みの経路であれば
            #最短経路探索用パラメータ設定
            try:
                self.point_dict[(lat, lon)]
                start_node=self.point_dict[(lat, lon)]
            except:
                start_point = (lat, lon)
                start_node = ox.distance.nearest_nodes(self.G, start_point[1], start_point[0])
                self.point_dict[(lat, lon)]=start_node
            
            try:
                self.point_dict[(self.last_pos[0], self.last_pos[1])]
                end_node=self.point_dict[(self.last_pos[0], self.last_pos[1])]
            except:
                end_point = (self.last_pos[0], self.last_pos[1])
                end_node = ox.distance.nearest_nodes(self.G, end_point[1], end_point[0])
                self.point_dict[(self.last_pos[0], self.last_pos[1])]=end_node

            
            #最短経路探索を実施
            try:
                #print(self.route_dict[(start_node,end_node)])
                shortest_path=self.route_dict[(start_node,end_node)]
            
            except:
                pass
                shortest_path = ox.shortest_path(self.G, start_node, end_node)
                self.route_dict[(start_node,end_node)]=shortest_path
            pass
            
            if shortest_path !=None:
                for i in shortest_path:

                    yield  self.G._node[i]['y'],self.G._node[i]['x']
            
                self.last_pos=[self.G._node[i]['y'],self.G._node[i]['x']]
            else:
                self.last_pos= [lat,lon]
        else:
            self.last_pos= [lat,lon]

class Sql_cont():
    def __init__(self) :
        DB_FILE = "../data.db"
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()
        try:
            self.cur.execute('DROP TABLE IF EXISTS reshape_route')
        except:
            pass
        self.cur.execute('create table if not exists  reshape_route (year,month,day,hour,minutes,seconds,flag,trajectories)')
    
    def insert(self,trajectories):
        bulk_data=list()
        for d in trajectories:
            bulk_data.append([d[0],d[1],d[2],d[3],d[4],d[5],d[6],str(d[7])])
        self.cur.executemany('INSERT INTO reshape_route (year,month,day,hour,minutes,seconds,flag,trajectories) values(?,?,?,?,?,?,?,?)',bulk_data)
        
        self.conn.commit()






if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sql=Sql_cont()
    setting=load_setting()#jsonファイルを読み込む
    print(str(setting))
    #実験結果を保存するディレクトリを読み込む

    routes=data_pipe.import_data(filename=setting["target"])#データをimport
    z=calc_area(routes)#演算を行う範囲を決定
    #a=[37.70149129294152,-122.52296739425346,37.80648357695361,-122.353516842315]
    z=[37.80648357695361,37.70149129294152,-122.353516842315,-122.52296739425346]

    

    route_cal=cal_route(z,setting)
    r=route_cal.calc(routes,setting["grid"])

    now=[routes[-1][3],routes[-1][4],routes[-1][5]]
    trajectory=list()
    trajectory.append(list())
    for route in routes[::-1]:
        
        #日付の切り替わりを判断
        if now[0]!=route[3] or now[1]!=route[4] or now[2]!=route[5]:
            print(now)
            sql.insert(trajectory[-1])
            now=[route[3],route[4],route[5]]
            trajectory.append(list())
            route_cal.reset()
            
            #SQLに１日ずつ保存する
        
        lat_lon=list()
        for node in route_cal.calc(route[0],route[1]):
            lat_lon.append( node )

        if len(lat_lon)!=0:
            trajectory[-1].append([route[3],route[4],route[5],route[6],route[7],route[8] , route[2],lat_lon])
        
        pass
    sql.insert(trajectory[-1])
    pass

    




