from jinja2 import pass_environment
import numpy as np
import sqlite3
from gym.envs.toy_text import discrete
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def db2trajectory(hour,apart):
    con = sqlite3.connect('../data.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM reshape_route WHERE "hour" == '+ str(hour)+" AND ""month""==5 ")
    #cur.execute('SELECT * FROM expart')
    #
    #z1---------z2
    #|           |
    #|           |
    #|           |
    #|           |
    #z3---------z4
    #z=[35.65, 139.98,35.71, 140.04]
    #delta=0.06
    
    #z=[37.47133,-122.50849500000001  ,37.87847, -122.10135500000001]
    #37.80648357695361, -122.52296739425346,37.70149129294152, -122.353516842315
    z=[37.70149129294152,-122.52296739425346,37.80648357695361,-122.353516842315]
    delta=z[2]-z[0]
    delta2=z[3]-z[1]
    #35.78138710841511, 140.05468028536765
    #35.60991173365618, 139.820534180286

    
    print((z[2]-z[0]),(z[3]-z[1]))
    #assert z[0]-z[2] == z[1]-z[3]
    #print(z[0]-z[2] , z[1]-z[3])
    xapart=[]
    yapart=[]

    grid=np.zeros([apart,apart])
    
    for i in range(apart):
        xapart.append(round(z[0]+delta/apart*i, 4))
        yapart.append(round(z[1]+delta2/apart*i, 4))
    
    first=cur.fetchone()
    now=[first[0],first[1],first[2]]
    trajectory=[]
    trajectory.append([])

    for row in cur:
        if now[0]!=row[0] or now[1]!=row[1] or now[2]!=row[2]:
            if len(trajectory[-1])!=0:
                trajectory.append([])
            now=[row[0],row[1],row[2]]
        #print(row[7],row[8])
        x=y=int()
        tr=eval(row[7])
        for t in tr:
            if t[0]<=z[2] and z[0]<=t[0] and  t[1]<=yapart[-1] and yapart[0]<=t[1]:
                for x in range(apart):
                    if t[0]<=xapart[x]:
                        break

                for y in range(apart):
                    if t[1]<=yapart[y] :
                        break
                
                #print(y,t[1])
                #print(x,y,xapart[x],yapart[y])

                grid[apart-x][y]+=1
                trajectory[-1].append(apart*apart-(x * apart - y))

    if len(trajectory[-1])==0:
        del trajectory[-1]

    
    con.close()
    trajectory2=list()
    for tr in trajectory:
        #print(t)
        tm=tr[0]
        trajectory2.append(list())
        for t in tr:
            if tm!=t:
                
                for f in move_fix(t,tm,apart):
                    trajectory2[-1].append(f)
                tm=t
        if len(trajectory2[-1])==0:
            del trajectory2[-1]
    

    return trajectory2,apart*apart

def move_fix(t,tm,apart):
    #斜め移動を判断し上下左右のみの移動に変更する
    if tm+apart==t or tm-apart==t or tm+1==t or tm-1==t:
        return [t]#斜めへの移動でなければ移動先を返す
    if tm+apart-1==t:#左斜め上
        return [t+1,t]
    if tm+apart+1==t:#右斜め上
        return [t-apart,t]
    if tm-apart-1==t:#左斜め下
        return [t+apart,t]
    if tm-apart+1==t:#右斜め下
        return [t-1,t]
    
    return [t]
    
        

    
#db2trajectory()