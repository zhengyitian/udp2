import uuid,time,json,random
import select,socket
import struct
from helpFunc  import *
from tornado import gen

class pullClient():
    def __init__(self,ip,port,sockMax,salt):
        self.sockMap = {}
        self.ip = ip
        self.port = port
        self.sockMax = sockMax
        self.packBuffer = {}
        self.currentPos = 0
        self.serverPos = 0
        self.salt = salt
        
    def refreshServerStatus(self,pos):
        if circleBig(self.serverPos,pos)==self.serverPos:
            return
        l = circleRange(self.serverPos,pos)
        for one in l:            
            self.packBuffer[one]={}
            self.packBuffer[one] ['missTimes'] = 0
            self.packBuffer[one]['con'] = ''
            self.packBuffer[one]['sendingTimes'] = 0
            self.packBuffer[one]['hasGot'] = False
        self.serverPos = pos
                
    def doWork(self,serverPos):
        if len(self.sockMap)!=0:
            rr = select.select(self.sockMap.keys(),[],[],0)
            if rr[0]!=[]:
                self.deal_rec(rr[0])
        self.deal_timeout()
        self.refreshServerStatus(serverPos)    
        self.resend()   
    
    def resend(self):
        l = circleRange(self.currentPos,self.serverPos)
        for one in l:
            if len(self.sockMap)>self.sockMax:
                break
            while  self.packBuffer[one]['sendingTimes']<=self.packBuffer[one]['missTimes'] and not self.packBuffer[one]['hasGot'] and self.packBuffer[one]['sendingTimes']<maxSending:
                self.packBuffer[one]['sendingTimes'] = self.packBuffer[one]['sendingTimes']+1
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                v = struct.pack('i',one)
                uuid ,msg = makePack(v,self.salt)
                s.sendto(msg, (self.ip, self.port))
                self.sockMap[s] = {'createTime':time.time(),'pack':one,'uuid':uuid}                

    @gen.coroutine
    def readBytes(self):
        s = ''
        while True :
            if self.currentPos not in self.packBuffer:
                yield gen.sleep(miniSleep)
                continue
            while True:        
                if self.currentPos not in self.packBuffer:
                    break              
                if not self.packBuffer[self.currentPos]['hasGot']:
                    break
                s += self.packBuffer[self.currentPos]['con']
                del self.packBuffer[self.currentPos]
                self.currentPos = circleAddOne(self.currentPos)
            if s!='':
                break
            yield gen.sleep(miniSleep)
        torRet(s)     
        
    def deal_rec(self,l):
        for s in l:
            j = s.recv(recLen)
            u = self.sockMap[s]['uuid']
            s2 = checkPackValid(j,u,self.salt)
            if not s2 or len(s2)<4:
                continue        
            s.close()
            pack = self.sockMap[s]['pack']
            del self.sockMap[s]
            if pack not in self.packBuffer:
                continue
            self.packBuffer[pack]['sendingTimes'] = self.packBuffer[pack]['sendingTimes']-1
            self.packBuffer[pack]['hasGot'] = True
            self.packBuffer[pack]['con'] = s2[4:]
        
    def deal_timeout(self):
        for s,v in  self.sockMap.items():
            ti = v['createTime']
            pack = v['pack']
            if ti+timeoutTime<time.time():
                s.close()
                del self.sockMap[s]
                if pack not in self.packBuffer:
                    continue 
                self.packBuffer[pack]['sendingTimes'] =  self.packBuffer[pack]['sendingTimes']-1
                self.packBuffer[pack]['missTimes'] = self.packBuffer[pack]['missTimes']+1
            

