from tornado import gen
import uuid,time,json,random
import select,socket,copy
from helpFunc import *

class pullServer():
    def __init__(self,port,toleranceTime,salt,isLocalTest=False):     
        self.lastTime = 0        
        self.ip = '0.0.0.0'
        self.port = port
        self.salt = salt
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0',self.port))  
        self.readBuffer = ''
        self.readBufferSize = 10*1024*1024
        self.currentPos = 0
        self.packBuffer = {}
        self.lock = False

    @gen.coroutine
    def sockRec(self):
        while True:
            r = select.select([self.sock],[],[],0)
            if not r[0]:
                return 
            data, addr = self.sock.recvfrom(recLen)
            uuid ,ss = checkPackValid_server(data,self.salt)
            if not uuid or isTest():
                continue
            pack = struct.unpack(ss[:4])[0]
            con = ss[4:]
            if circleBig(self.currentPos,pack)==self.currentPos:
                continue
            m = {}
            m['con'] = con            
            self.packBuffer[pack]=m            
            j = 'got'
            data = makePack_server(j, uuid, self.salt)
            if isTest():
                continue
            if isLocalTest:
                yield gen.sleep(random.randint(200,300)/1000.0)
                self.sock.sendto(data,addr)
                
    @gen.coroutine
    def refreshServerStatus(self):
        while self.lock:
            yield gen.sleep(miniSleep)
        self.lock = True
        tempPos = self.currentPos
        while  tempPos in self.packBuffer:
            tempPos = circleAddOne(tempPos)
        l = circleRange(self.currentPos,tempPos)
        for one in l:
            while len(self.readBuffer)>self.readBufferSize:
                yield gen.sleep(miniSleep)
            self.readBuffer += self.packBuffer[one]['con']
            del self.packBuffer[one]
        self.currentPos = tempPos
        self.lock = False
        
    @gen.coroutine
    def doWork(self):
        yield self.sockRec()
        yield self.refreshServerStatus()
