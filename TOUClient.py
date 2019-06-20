import socket,select
from helpFunc import *
import uuid,json
mySalt = serviceSaltKey
import os,sys
runningPath = os.path.split(__file__)[0]
from TOUManagerClient import TOUManagerClient
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    id = str(uuid.uuid1())
    m = {'sign':id}
    j = json.dumps(m)
    u ,s2 = makePack(j,mySalt)    
    sock.sendto(s2, (serverIp, servicePort))
    r = select.select([sock],[],[],timeoutTime)
    if r[0]==[]:
        sock.close()
        continue
    j = sock.recv(recLen)
    s2 = checkPackValid(j,u,mySalt)
    if not s2:
        sock.close()
        continue 
    m = json.loads(s2)
    salt,s1,s2,s3 = m['con']
    print 'server starts:',salt,s1,s2,s3
    sock.close()
    break
from tornado.ioloop import IOLoop
t = TOUManagerClient(serverIp, [s1,s2,s3], salt, clientListenIp, clientListenPort)
IOLoop.instance().add_callback(t.turnUp)    
IOLoop.instance().start()

   
