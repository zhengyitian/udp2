from tornado import gen
from pushServer import pushServer
from pullServer import pullServer
from statusServer import statusServer
from tornado.ioloop import PeriodicCallback

#start by some policy(like start on the server first ,then on the client),
#process exits  auto when no heartbeats.

class UStreamServer():
    def __init__(self):
        self.status = statusServer(9993,3,'salt')
        self.pull = pullServer(9994,'salt')
        self.push = pushServer(9995,'salt')
        PeriodicCallback(self.doWork,10)
        pass
    
    @gen.coroutine
    def doWork(self):
        yield self.status.doWork()   
        m = yield self.status.getClientStatus()
        pos = m
        self.pull.setClientPos(pos)
        yield self.pull.doWork()
        yield self.push.doWork()
        pos = yield self.push.refreshServerStatus()
        yield self.status.setServerStatus(pos)
    
    @gen.coroutine
    def start(self):
        yield self.status.getClientStatus()
    
    @gen.coroutine
    def read(self):
        yield self.push.read()        
    
    @gen.coroutine
    def write(self,s):
        yield self.pull.write(s)
