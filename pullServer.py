from tornado import gen
import uuid,time,json,random
import select,socket,copy
from helpFunc import *

class pullServer():
    def __init__(self,port,salt,isLocalTest=False):     
        self.lastTime = 0        
        self.ip = '0.0.0.0'
        self.port = port
        self.salt = salt
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0',self.port))  
        self.readBuffer = ''
        self.readBufferSize = 10*1024*1024
        self.currentPos = 0
        self.packBuffer = {}
        self.lock = False
        self.isWriting = False
        self.clientPos = 0

    def sockRec(self):
        while True:
            r = select.select([self.sock],[],[],0)
            if not r[0]:
                return 
            data, addr = self.sock.recvfrom(recLen)
            uuid ,ss = checkPackValid_server(data,self.salt)
            if not uuid or isTest():
                continue
            l = circleRange(self.clientPos,self.currentPos)
            re = ''
            pack = struct.unpack('i',ss)[0]
            if pack not in l:
                re = '0'                
            else:
                re = struct.pack('i',pack)+self.packBuffer[pack]['con']            
            data = makePack_server(re, uuid, self.salt)
            if isTest():
                continue            
            self.sock.sendto(data,addr)

    def setClientPos(self,pos):
        if circleBig(self.clientPos,pos) == self.clientPos:
            return
        l = circleRange(self.clientPos,pos)
        for one in l:
            del self.packBuffer[one]
        self.clientPos = pos 
            
    @gen.coroutine
    def write(self,s):
        if self.isWriting:
            raise Exception
        self.isWriting = True
        
        while True:
            bigPos = circleBig(self.currentPos,circleAdd(self.clientPos,pushAhead))            
            canRecPack = len(circleRange(self.currentPos,bigPos))
            canRecBytes = packLimit*canRecPack
            if s<= canRecBytes:
                s1 = s
                s = ''
            else:
                s1 = s[:canRecBytes]
                s = s[canRecBytes:]          
            l = cut_text(s1,packLimit)
            if l[-1] == '':
                l = l[:-1]                
            for one in l:
                self.packBuffer[self.currentPos] = {}
                self.packBuffer[self.currentPos]['con'] = one
                self.currentPos = circleAddOne(self.currentPos)        
            if s=='':
                break
            yield gen.sleep(miniSleep)                    
        self.isWriting = False
        

    def doWork(self):
        self.sockRec()
