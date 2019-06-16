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
g_port = 9993

global serverMap
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0',g_port))  
    while True :
        r = select.select([sock],[],[],selectTime)
        if not r[0]:
            return
        data, addr = sock.recvfrom(recLen)
        m = json.loads(data)
        ti = m['time']
        if ti>lastTime:
            v = m['con']
            print time.time(),v
        v = re_get('b')
        m = {'time':time.time(),'con':v}
        j = json.dumps(m)
        sock.sendto(j,addr)
main()
