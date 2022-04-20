import os
import numpy as np
import json
from tqdm import tqdm
import numpy as np
import osmnx as ox
ox.config(use_cache=True, log_console=True)
import rc_lib.data_pipe  as data_pipe
def load_setting():#jsonファイルを読み込む
    json_open = open('settings.json', 'r')
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

    # print(z[0],z[1],z[2],z[3])
    return z

class cal_route:
    def __init__(self,z) :
        #z=[35.65, 139.98,35.71, 140.04]#頂点を指定
        self.G = ox.graph_from_bbox(z[1],z[3],z[0] ,z[2], network_type='drive')
        self.fmap = ox.plot_graph_folium(self.G)
        self.last_pos=[0,0]
        self.route_dict={}
        self.point_dict={}

    def calc(self,lat,lon):
        pass
        #print("val")
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
                #print([lat,lon])
                #yield lat,lon
        else:
            self.last_pos= [lat,lon]
            #print([lat,lon])
            #yield lat,lon

def onehot_feature(routes,states):
        features = np.zeros(states)#特徴量ベクトルを宣言(use env)
        for i in routes:#各軌道データごとで回す
            for s in i:#各軌道から1stepごと
                features[s] += 1#0~nまでの訪問回数をカウント

        features /= len(routes)#平均訪問回数を計算(特殊な計算式だが、リスト内の各要素に対して割り算を行っているだけ)1/M*Σfs
        return features#平均訪問回数を返えす



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    setting=load_setting()#jsonファイルを読み込む
    print(str(setting))
    routes=data_pipe.import_data(filename=setting["target"])#データをimport
    z=calc_area(routes)#演算を行う範囲を決定
    print(z)

    #平均訪問回数を可視化
    #a=onehot_feature(routes,setting["grid"])

    route_cal=cal_route(z)
    r=route_cal.calc(routes,setting["grid"])

    for route in routes[::-1]:
        print(route)
        pass
    pass

    




