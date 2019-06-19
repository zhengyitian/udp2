from tornado import gen
from pushClient import pushClient
from pullClient import pullClient
from statusClient import statusClient
from tornado.ioloop import PeriodicCallback

#start by some policy(like start on the server first ,then on the client),
#process exits  auto when no heartbeats.

class UStreamClient():
    def __init__(self):
        ip = '0.0.0.0'
        self.status = statusClient(ip,9993,5,3,'salt')
        self.pull = pullClient(ip,9994,495,'salt')
        self.push = pushClient(ip,9995,495,'salt')
        PeriodicCallback(self.doWork,10)
        
    @gen.coroutine
    def doWork(self):
        yield self.status.doWork()   
        m = yield self.status.getServerStatus()
        self.pull.doWork(m)
        self.push.doWork(m)
        m2 = {}
        yield self.status.setClientStatus(m2)    
        
    @gen.coroutine
    def start(self):
        yield self.status.getServerStatus()

    
    @gen.coroutine
    def read(self):
        yield self.pull.readBytes()

    
    @gen.coroutine
    def write(self,s):
        yield self.push.write(s)
