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
g_port = 9994
sockMax = 500
packBuffer = {}
bufferSize = 1000
clientCacheKey = 'clientCacheKey'
clientCacheLockKey = 'clientCacheLockKey'
clientServerReadKey = 'clientServerReadKey'
currentPos = 0
serverPos = 0
packLimit = 700
maxSending = 5
import struct
import re as re3
def cut_text(text,lenth): 
    textArr = re3.findall('.{'+str(lenth)+'}', text) 
    textArr.append(text[(len(textArr)*lenth):]) 
    return textArr

isSending = {}
re_set(clientServerReadKey,'')
def circleBig(a,b):
    if a==b:
        return False
    if a>b and (a-b)<(bufferSize/2):
        return True
    if a<b and (b-a)>(bufferSize/2):
        return True
    return False

def circleRange(a,b):  # return [,)  same as range
    temp = a
    ret = []
    while True:
        if not circleBig(b,temp):
            break
        ret.append(temp)
        temp = circleAdd(temp,1)
    return ret
def circleMax(l):
    ret = None
    k = l.keys()
    for i in k:
        if ret==None:
            ret = i
        if circleBig(i,ret):
            ret = i
    return ret


def circleAddOne(a):
    if a == bufferSize-1:
        return 0
    return a+1

def circleAdd(a,b):
    ret = a
    for i in range(b):
        ret = circleAddOne(ret)
    return ret


pushAhead = 100

#work to do: check rev pack valid
#dk = hashlib.pbkdf2_hmac('sha256', b'password', b'saltxx', 1000)
#print time.time(),binascii.hexlify(dk)

def deal_rec(l):
    global sockMap,packBuffer
    for s in l:
        j = s.recv(recLen)
        s.close()
        pack = sockMap[s]['pack']
        del sockMap[s]
        if pack not in packBuffer:
            continue
        packBuffer[pack]['sendingTimes'] = packBuffer[pack]['sendingTimes']-1
        packBuffer[pack]['hasGot'] = True


def deal_timeout():
    global sockMap,packBuffer
    for s,v in  sockMap.items():
        ti = v['createTime']
        pack = v['pack']
        if ti+timeoutTime<time.time():
            s.close()
            del sockMap[s]
            if pack not in packBuffer:
                continue 
            packBuffer[pack]['sendingTimes'] = packBuffer[pack]['sendingTimes']-1
            packBuffer[pack]['missTimes'] = packBuffer[pack]['missTimes']+1
            

def resend():
    global sockMap,packBuffer,serverPos,currentPos
    j = re_get(clientServerReadKey)
    if not j:
        m = {'pos':0}
    else:
        m = json.loads(j)
    pos = m['pos']
    l = circleRange(serverPos,pos)
    for one in l:
        del packBuffer[one]
    serverPos = pos
    bigPos = circleAdd(pos,pushAhead)
    canRecPack = len(circleRange(currentPos,pushAhead))
    canRecBytes = packLimit*canRecPack
    s = re_get(clientCacheKey)
    if not s:
        s = ''
    s1 = ''
    s2 = ''
    if s<= canRecBytes:
        s1 = s
        s2 = ''
    else:
        s1 = s[:canRecBytes]
        s2 = s[canRecBytes:]
    re_set(clientCacheKey,s2)
    l = cut_text(s1,packLimit)
    for one in l:
        packBuffer[currentPos] = {}
        packBuffer[currentPos] ['missTimes'] = 0
        packBuffer[currentPos]['con'] = one
        packBuffer[currentPos]['sendingTimes'] = 0
        packBuffer[currentPos]['hasGot'] = False
        currentPos += 1
    l = circleRange(pos,currentPos)
    for one in l:
        if len(sockMap)>sockMax:
            break
        while  packBuffer[one]['sendingTimes']<=packBuffer[one]['missTimes'] and not packBuffer[one]['hasGot'] and packBuffer[one]['sendingTimes']<maxSending:
            packBuffer[one]['sendingTimes'] = packBuffer[one]['sendingTimes']+1
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            v = struct.pack('i',one)+packBuffer[one]['con']
            s.sendto(v, (g_ip, g_port))
            sockMap[s] = {'createTime':time.time(),'pack':one}                

def main():
    global sockMap
    while True:
        if len(sockMap)!=0:
            rr = select.select(sockMap.keys(),[],[],selectTime)
            if rr[0]!=[]:
                deal_rec(rr[0])
        deal_timeout()
        
        resend()
main()
        
