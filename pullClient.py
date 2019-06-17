import uuid,time,json,random
import select,socket
import struct
from helpFunc  import *

miniSleep = 0.01
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
clientPullCacheKey = 'clientPullCacheKey'
clientServerWriteKey = 'clientServerWriteKey'
clientClientReadKey = 'clientClientReadKey'
re_set(clientPullCacheKey, '')
re_set(clientServerWriteKey, '')
re_set(clientClientReadKey, '')

currentPos = 0
serverPos = 0

packLimit = 700
maxSending = 5
canCacheNum = 100
salt = 'salt'
def refreshServerStatus():
    global serverPos
    j = re_get(clientServerWriteKey)
    if not j:
        m = {'pos':0}
    else:
        m = json.loads(j)
    serverPos = m['pos']
  

def refreshClientStatus():
    l = circleRange(serverPos,pos)
    for one in l:
        del packBuffer[one]
    serverPos = pos
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
    l = circleRange(currentPos,serverPos)
    for one in l:
        if len(sockMap)>sockMax:
            break
        while  packBuffer[one]['sendingTimes']<=packBuffer[one]['missTimes'] and not packBuffer[one]['hasGot'] and packBuffer[one]['sendingTimes']<maxSending:
            packBuffer[one]['sendingTimes'] = packBuffer[one]['sendingTimes']+1
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            v = struct.pack('i',one)
            uuid ,msg = makePack(v,salt)
            s.sendto(msg, (g_ip, g_port))
            sockMap[s] = {'createTime':time.time(),'pack':one,'uuid':uuid}                
def main():
    global sockMap
    while True:
        if len(sockMap)!=0:
            rr = select.select(sockMap.keys(),[],[],selectTime)
            if rr[0]!=[]:
                deal_rec(rr[0])
        deal_timeout()
        refreshClientStatus()        
        refreshServerStatus()
        resend()
main()
        
