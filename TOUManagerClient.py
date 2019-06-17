from collections import deque

queueMaxSize = 100000
from UStreamClient import UStreamClient

from tornado.ioloop import IOLoop
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer
import functools,time
from tornado.ioloop import PeriodicCallback

import json
import base64

class TOUManagerClient(TCPServer):
    def __init__(self):
        super(TOUManagerClient,self).__init__()
        self.ustream = UStreamClient()
        self.ustream.start()
        work1  = PeriodicCallback(self.stream_to_queue,10)
        work1.start()
        work2  = PeriodicCallback(self.queue_to_stream,10)
        work2.start()      
        self.queueInput = deque()
        self.queueOutput = deque()
        self.listen(9999,'0.0.0.0')
        
    @gen.coroutine
    def addTask(self): # pack to queue
        #size limits,so it may wait.
        pass
    @gen.coroutine
    def waitTaskBack(self):
        pass
    @gen.coroutine
    def handle_stream(self, stream, address):
        pack = connPack
        id = yield self.addTask(pack)
        back = yield self.waitTaskBack(id)
        if back['ret'] = 0:
            return
        conn_seq = back['conn_seq']
        
        #each conn_seq has two parts. when they all close, the conn close.
        #we can delete it after send the info to server.
        
        IOLoop.instance().add_callback(functools.partial(self.doRead,stream,readS))
        IOLoop.instance().add_callback(functools.partial(self.doWrite,stream,writeS))
        
    @gen.coroutine
    def getReadPacks(self,conn_seq):
        #background worker gets ustream to queue,
        pass
    @gen.coroutine
    def doWrite(self,stream,conn_seq):
        while True:
            try:
                while True:
                    d1 = yield stream.read_bytes(1)
                    if len(d1)!=0:
                        break
                data =  stream._read_buffer
                l = len(data)
                d2 = yield stream.read_bytes(l-1)
            except:
                #send a pack to server, 
                #close one part of the conn. if two parts all close, clean up
                return        
            try:
                #check how much has been write but no reply.
                #if too much ,wait
                #if write excption happens, it is got here.
                yield self.addTask(d1+d2)
            except:
                #close one part of the conn. if two parts all close, clean up
                return
            
    @gen.coroutine
    def doRead(self,stream,conn_seq):
        while True:
            s = yield self.getReadPacks(conn_seq)
            if not s:
                #close one part of the conn. if two parts all close, clean up
                return
    
            try:
                yield stream.write(d1)
                #send a pack to server,so it knows it can write more.
                
            except:
                #send a pack to server, 
                #close one part of the conn. if two parts all close, clean up
                return
        
    @gen.coroutine
    def stream_to_queue(self):
        pass
    
    @gen.coroutine
    def queue_to_stream(self):
        pass
    

if __name__ == "__main__":
    TOUManagerClient()
    IOLoop.instance().start()
    







