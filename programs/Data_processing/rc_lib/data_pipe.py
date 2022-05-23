import datetime
import re


def conv_time(stamp):
    pass
    #'2020-09-21T01:22:18.428Z'
    result = re.split(r'[-T:.Z]', stamp)
    #print(result)
    return result

def import_data(filename):
    
    f = open(filename, 'r')
    datalist = f.readlines()

    data=list()#データ格納用
    for d in datalist:
        pass
        d=d.replace( '\n' , '' )
        d=[float(r) for r in d.split(" ")]
        date=datetime.datetime.fromtimestamp(d[3])
        data.append([d[0],d[1],d[2],date.year,date.month,date.day,date.hour,date.minute,date.second])
    
    return data

    