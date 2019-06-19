import uuid,time,json,random
import select,socket
import struct
from helpFunc  import *
from tornado import gen

class pushClient():
    def __init__(self,ip,port,sockMax,salt):
        self.sockMap = {}
        self.ip = ip
        self.port = port
        self.sockMax = sockMax
        self.packBuffer = {}
        self.currentPos = 0
        self.serverPos = 0
        self.salt = salt

        
    def deal_rec(self,l):
        for s in l:
            j = s.recv(recLen)
            u = self.sockMap[s]['uuid']
            s2 = checkPackValid(j,u,self.salt)
            if not s2 :
                continue                    
            s.close()
            pack =  self.sockMap[s]['pack']
            del  self.sockMap[s]
            if pack not in  self.packBuffer:
                continue
            self.packBuffer[pack]['sendingTimes'] =  self.packBuffer[pack]['sendingTimes']-1
            self.packBuffer[pack]['hasGot'] = True    
    
    def deal_timeout(self):
        for s,v in  self.sockMap.items():
            ti = v['createTime']
            pack = v['pack']
            if ti+timeoutTime<time.time():
                s.close()
                del self.sockMap[s]
                if pack not in self.packBuffer:
                    continue 
                self.packBuffer[pack]['sendingTimes'] = self.packBuffer[pack]['sendingTimes']-1
                self.packBuffer[pack]['missTimes'] = self.packBuffer[pack]['missTimes']+1                
    
    def refreshServerStatus(self,pos):
        while self.serverPos in self.packBuffer and self.packBuffer[self.serverPos]['hasGot']:
            del self.packBuffer[self.serverPos]
            self.serverPos = circleAdd(self.serverPos,1)        
        if circleBig(self.serverPos,pos)==self.serverPos:
            return        
        l = circleRange(self.serverPos,pos)
        for one in l:
            del self.packBuffer[one]
        self.serverPos = pos          
        
    @gen.coroutine
    def write(self,s):
        while s:
            bigPos = circleBig(self.currentPos,circleAdd(self.serverPos,pushAhead))            
            canRecPack = len(circleRange(self.currentPos,bigPos))
            if canRecPack==0:
                yield gen.sleep(miniSleep)
                continue
                
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
                self.packBuffer[self.currentPos] ['missTimes'] = 0
                self.packBuffer[self.currentPos]['con'] = one
                self.packBuffer[self.currentPos]['sendingTimes'] = 0
                self.packBuffer[self.currentPos]['hasGot'] = False             
                self.currentPos = circleAddOne(self.currentPos)

        
    def resend(self):       
        l = circleRange(self.serverPos,self.currentPos)
        for one in l:
            if len(self.sockMap)>self.sockMax:
                break
            while  self.packBuffer[one]['sendingTimes']<=self.packBuffer[one]['missTimes'] and not self.packBuffer[one]['hasGot'] and self.packBuffer[one]['sendingTimes']<maxSending:
                self.packBuffer[one]['sendingTimes'] = self.packBuffer[one]['sendingTimes']+1
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                v = struct.pack('i',one)+self.packBuffer[one]['con']
                uuid , con = makePack(v,self.salt)
                s.sendto(con, (self.ip, self.port))
                self.sockMap[s] = {'createTime':time.time(),'pack':one,'uuid':uuid}                
    
    def doWork(self,serverPos):
        if len(self.sockMap)!=0:
            rr = select.select(self.sockMap.keys(),[],[],0)
            if rr[0]!=[]:
                self.deal_rec(rr[0])
        self.deal_timeout()        
        self.refreshServerStatus(serverPos)      
        self.resend()
    
            
