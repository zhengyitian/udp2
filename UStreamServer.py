from tornado.ioloop import IOLoop
from tornado import gen
from pushServer import pushServer
from pullServer import pullServer
from statusServer import statusServer
from tornado.ioloop import PeriodicCallback
import time,functools,random
from helpFunc import *

class UStreamServer():
    def __init__(self,ip,port,salt):
        self.status = statusServer(ip,port,3,salt)
        self.status.serverStatus = {'serverPushPos':0,'serverPullPos':0}
        self.status.clientStatus = {'clientPushPos':0,'clientPullPos':0}        
        self.pull = pullServer(ip,port+1,salt)
        self.push = pushServer(ip,port+2,salt)
        IOLoop.instance().add_callback(self.doWork)
        IOLoop.instance().add_callback(self.keepStatus)
        w2 = PeriodicCallback(self.keepAlive,keepAliveTimer)
        w2.start()     
        self.startTime = time.time()
        
    def keepAlive(self):
        la = self.status.lastUpdateTime
        if (la==0 and self.startTime<time.time()-heartbeatLimit) or (la!=0 and la<time.time()-heartbeatLimit) :
            import sys
            print 'error'
            sys.exit(0)       
            
    @gen.coroutine
    def keepStatus(self):
        while True:
            yield gen.sleep(miniSleep)          
            self.status.doWork() 
        
    @gen.coroutine
    def doWork(self):
        while True:
            yield gen.sleep(miniSleep)          
            m = yield self.status.getClientStatus()
            pos = m['clientPullPos']
            self.pull.setClientPos(pos)
            self.pull.doWork()
            self.push.doWork()
            pos = self.push.refreshServerStatus()
            m = {'serverPushPos':pos,'serverPullPos':self.pull.currentPos}
            yield self.status.setServerStatus(m)
    
    @gen.coroutine
    def start(self):
        yield self.status.getClientStatus()
    
    @gen.coroutine
    def read(self):
        s = yield self.push.read()        
        torRet(s)
    
    @gen.coroutine
    def write(self,s):
        yield self.pull.write(s)
        
co = 0  
g_ss = ''
@gen.coroutine
def doRead(t):
    global co
    while True:
        yield gen.sleep(miniSleep)
        s = yield t.read()
        co += len(s)
        global g_ss
        g_ss+= s
        msg = TOUMsg()
        r,g_ss = msg.unpack(g_ss)
        if r:
            print 'got msg'
        else:
            print 'not msg'
        print time.time(),co,s[:20]     

@gen.coroutine
def doWrite(t):
    while True:
        yield gen.sleep(miniSleep)
        msg = TOUMsg({},'s'*random.randint(10000,20000))
        yield t.write(msg.pack())          

@gen.coroutine
def main(t):
    yield t.start()
    IOLoop.instance().add_callback(functools.partial(doRead,t))
    IOLoop.instance().add_callback(functools.partial(doWrite,t))

if __name__ == "__main__":
    t = UStreamServer()
    IOLoop.instance().add_callback(functools.partial(main,t))    
    IOLoop.instance().start()