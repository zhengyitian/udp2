from tornado.ioloop import IOLoop
from tornado import gen
from pushClient import pushClient
from pullClient import pullClient
from statusClient import statusClient
from tornado.ioloop import PeriodicCallback
import time,functools,random
from helpFunc import *

class UStreamClient():
    def __init__(self):
        ip = '0.0.0.0'
        ip = '144.202.17.72'
        self.status = statusClient(ip,9993,5,3,'salt')
        self.status.serverStatus = {'serverPushPos':0,'serverPullPos':0}
        self.status.clientStatus = {'clientPushPos':0,'clientPullPos':0}
        self.pull = pullClient(ip,9994,495,'salt')
        self.push = pushClient(ip,9995,495,'salt')
        IOLoop.instance().add_callback(self.keepStatus)
        IOLoop.instance().add_callback(self.doWork)   
        w2 = PeriodicCallback(self.keepAlive,10)
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
            m = yield self.status.getServerStatus()
            p1 = m['serverPullPos']
            p2 = m['serverPushPos']
            self.pull.doWork(p1)
            self.push.doWork(p2)
            m2 = {'clientPullPos':self.pull.currentPos}
            yield self.status.setClientStatus(m2)    
        
        
    @gen.coroutine
    def start(self):
        yield self.status.getServerStatus()
    
    @gen.coroutine
    def read(self):
        s = yield self.pull.readBytes()
        torRet(s)
        
    @gen.coroutine
    def write(self,s):
        yield self.push.write(s)
        
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
    t = UStreamClient()
    IOLoop.instance().add_callback(functools.partial(main,t))    
    IOLoop.instance().start()