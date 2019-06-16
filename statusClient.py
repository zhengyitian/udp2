import redis
from tornado import gen
import uuid,time,json,random
import select,socket
miniSleep = 0.01
conn = redis.Redis(host='localhost', port=6379, db=0)
def re_get(k):
    global conn
    try:
        return conn.get(k)
    except:
        conn = redis.Redis(host='localhost', port=6379, db=0)
        return conn.get(k)        

def re_set(k,s):
    global conn
    try:
        conn.set(k,s)
    except:
        conn = redis.Redis(host='localhost', port=6379, db=0)
        conn.set(k,s)
def re_del(k):
    global conn
    try:
        conn.delete(k)
    except:
        conn = redis.Redis(host='localhost', port=6379, db=0)
        conn.delete(k)

sleepTime = 0.1
sockMap = {}
selectTime = 0.1
inRoadNum = 5
recLen = 10240
lastTime = 0
timeoutTime = 0.7
g_ip = '127.0.0.1'
g_ip = '144.202.17.72'
g_port = 9993
def deal_rec(l):
    global sockMap
    for s in l:
        j = s.recv(recLen)
        s.close()
        del sockMap[s]
        m = json.loads(j)
        ti = m['time']
        if ti>lastTime:
            v = m['con']
            print time.time(),v

def deal_timeout():
    global sockMap
    for k ,v in  sockMap.items():
        ti = v['createTime']
        if ti+timeoutTime<time.time():
            k.close()
            del sockMap[k]
def resend():
    global sockMap
    n = inRoadNum - len(sockMap)
    for i in range(n):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        v = re_get('a')
        m = {'time':time.time(),'con':v}
        j = json.dumps(m)
        s.sendto(j, (g_ip, g_port))
        sockMap[s] = {'createTime':time.time()}
        
def readA():
    global sockMap
    while True:
        if len(sockMap)!=0:
            rr = select.select(sockMap.keys(),[],[],selectTime)
            if rr[0]!=[]:
                deal_rec(rr[0])
        deal_timeout()
        resend()
readA()
        
    