import networkx as nx
import matplotlib.pyplot as plt
import os
import numpy as np
grid_n=60
#from RL_1.main import print_data

def create_network(_ngrid):
    ngrid = _ngrid
    G = nx.grid_graph(dim=[ngrid, ngrid])
    nx.draw(G,pos=dict((n, n) for n in G.nodes()),node_size=20)

    return G

def importdata(n):#エクセルからデータを抽出する
    ac=grid_n
    array=list()
    import openpyxl
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    wb = openpyxl.load_workbook("./input_data/result/result"+str(n)+".xlsx")
    ws = wb.worksheets[0]
    x=0
    y=0

    for i in range(ac):
        array.append(list())
        for j in range(ac):
            a=ws.cell(1+(i*ac)+j, 2)
            array[i].append(a.value)
    
    return np.flipud(array)

def cal_reward(start,goal,map,G):
    pass
    lim=grid_n
    s=(int(start%lim),int(start/lim))
    g=(int(goal%lim),int(goal/lim))
    route = nx.shortest_path(G, source=s, target=g)
    #print(s,g,route)
    reward=0
    for r in route:
        #print(s)
        #print(map[s])
        reward+=map[r]

    #print(start , s)
    
    return start,goal,reward,len(route),route

import sqlite3

class Sql_controller():
    def __init__(self,name=None,n=None):
        if name:
            dbname=str(name)
        else:
            dbname = 'main.db'

        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

        self.n=n

        # テーブルの作成
        self.cur.execute(
            'CREATE TABLE if not exists routes_reward'+str(self.n)+'(id INTEGER PRIMARY KEY AUTOINCREMENT, startpos STRING,goalpos STRING, reward INTEGER ,step INTEGER , route STRING)'
        )
        self.bulktable=list()

    def insert(self,values):#遅いので複数ある場合はバルクインサート

        self.bulktable.append(values)
        if len(self.bulktable)>=10000:
            self.bulkinsert()
            self.bulktable=list()

    
    def bulkinsert(self):
        self.cur.executemany('INSERT INTO routes_reward'+str(self.n)+' ( startpos, goalpos, reward ,step ,route ) values(?, ?, ?, ?, ? )',self.bulktable)

        self.conn.commit()


if __name__ == '__main__':
    from tqdm import tqdm
    import copy
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    state=grid_n*grid_n
    

    import math
    
    G=create_network(int(math.sqrt(state)))
    

    states=list()
    st=list()
            
    #24it
    for n in range(24):
        rewards=importdata(n=n)
        st=list()
        #閾値を計算
        for y in range(grid_n):
            for x in range(grid_n):
                st.append(rewards[x,y])
        
        round_value=sum(st)/len(st)*20
        #print(round_value)

        for y in range(grid_n):
            for x in range(grid_n):
                #print(rewards[x,y])
                if rewards[x,y] >=round_value:
                    states.append(x+y*grid_n)
                    if x+y*grid_n==1598:
                        pass
    
    states=list(set(states))
    states.sort()

    print(len(states))
    pass
            

    for h in range(24):
        Gs=list()
        sql=Sql_controller(n=h)
        rewards=importdata(h)
        for i in range(100,0,-5):
            G2=copy.deepcopy(G)
            nodes_to_remove=list()
            for y in range(grid_n):
                for x in range(grid_n):
                    if rewards[x,y] <i/100:
                        nodes_to_remove.append((x,y))

            G2.remove_nodes_from(nodes_to_remove)
            Gs.append(G2)
        nx.draw(Gs[-1],pos=dict((n, n) for n in G2.nodes()),node_size=20,width=10)
        plt.axis('equal')
        #plt.show()
        Gs.append(G)

        for i,s in tqdm(enumerate(states)):
            
            for g in states:
                for q in Gs:
                    try:
                        start,gola,reward,step,route=cal_reward(s,g,rewards,q)
                        break
                    except:
                        pass
                sql.insert([start,gola,reward,step,str(route)])

        sql.bulkinsert()