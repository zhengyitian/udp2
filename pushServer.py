from tornado import gen
import uuid,time,json,random
import select,socket,copy
from helpFunc import *

class pushServer():
    def __init__(self,ip,port,salt,isLocalTest=False):     
        self.lastTime = 0        
        self.ip = ip
        self.port = port
        self.salt = salt
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip,self.port))  
        self.readBuffer = ''
        self.readBufferSize = streamBufferSize
        self.currentPos = 0
        self.packBuffer = {}
        self.lock = False
        self.isReading = False
        self.testRecord = 0
        self.testCache = ''
        
    def sockRec(self):
        while True:
            r = select.select([self.sock],[],[],0)
            if not r[0]:
                return 
            data, addr = self.sock.recvfrom(recLen)
            uuid ,ss = checkPackValid_server(data,self.salt)
            if not uuid or isTest():
                continue
            pack = struct.unpack('i',ss[:4])[0]

            con = ss[4:]
            if circleBig(self.currentPos,pack)!=pack:
                data = makePack_server('0', uuid, self.salt)
                self.sock.sendto(data,addr)                
                continue
            m = {}
            m['con'] = con            
            self.packBuffer[pack]=m            
            j = 'gott'
            data = makePack_server(j, uuid, self.salt)
            if isTest():
                continue
            self.sock.sendto(data,addr)
                
    
    def refreshServerStatus(self):
        while len(self.readBuffer)<self.readBufferSize and self.currentPos in self.packBuffer:
            self.readBuffer += self.packBuffer[self.currentPos]['con']        
            del self.packBuffer[self.currentPos]
            self.currentPos = circleAddOne(self.currentPos)
        return self.currentPos
        
    @gen.coroutine
    def read(self):
        if self.isReading:
            raise Exception
        self.isReading = True
        while self.readBuffer == '':
            yield gen.sleep(miniSleep)
        s = self.readBuffer
        self.readBuffer = ''
        self.isReading = False
        torRet(s)
        

    def doWork(self):
        self.sockRec()
        
        