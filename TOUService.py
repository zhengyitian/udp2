from helpFunc import *
import os,sys,time,json

from collections import deque

runningPath = os.path.split(os.path.realpath(__file__))[0]
print runningPath  
mySalt = serviceSaltKey
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((serviceIp,servicePort))
usedMap = {}
usedQ = deque()

while True:
    data, addr = sock.recvfrom(recLen)
    uuid ,ss = checkPackValid_server(data,mySalt)
    if not uuid :
        continue
    m = json.loads(ss)
    sign = m['sign']
    r = ''
    if sign not in usedMap:
        s1,s2,s3 = find3Ports()
        time.sleep(0.1)
        salt = randomStringDigits()
        os.system('nohup python %s/TOUManagerServer.py %s %s %s %s &'%(runningPath,salt,s1,s2,s3))
        print 'start server:',salt,s1,s2,s3
        m = {'con':(salt,s1,s2,s3),'createTime':time.time()}
        usedMap[sign] = m
        usedQ.append(sign)
        if len(usedMap)>10000:
            ss = usedQ.popleft()
            del usedMap[ss]
            
    m = usedMap[sign]
    j = json.dumps(m)
    data = makePack_server(j, uuid, mySalt)
    sock.sendto(data,addr)
    #from TOUManagerServer import TOUManagerServer
    #from tornado.ioloop import IOLoop
    #t = TOUManagerServer(serverListenIp,[s1,s2,s3],salt,redirTcpIp,redirTcpPort)
    #IOLoop.instance().add_callback(t.turnUp)    
    #IOLoop.instance().start()            
    
   