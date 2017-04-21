# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 22:32:01 2015

@author: zech
"""
import asyncio
import zmq.asyncio
import zmq
import pickle
import logging
import logging.handlers
import socketserver
import struct
import sys

from zmq.log.handlers import PUBHandler

class SimpleQuantLogger(logging.Logger):
    def __init__(self, topic, loggerServerAddr, newLoop=False):
        super().__init__(topic)
        self.name = topic

        if isinstance(loggerServerAddr, str):
            addr = loggerServerAddr.split(':')
            host, port = addr if len(addr) == 2 else (addr[0], None)
        self.loggerServerHost = host
        self.loggerServerPort = port

        context = zmq.asyncio.Context()

        # a new loop
        if newLoop:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        publisher = context.socket(zmq.PUB)
        publisher.connect('tcp://%s:%s' %(self.loggerServerHost, self.loggerServerPort))
        handler = PUBHandler(publisher)
        handler.root_topic = topic
        self.addHandler(handler)
        logging.basicConfig(
            level=logging.INFO,
            format='PID %(process)5s %(name)18s: %(message)s',
            stream=sys.stderr,
        )



class SimpleQuantLoggerServer():
    def __init__(self, addr, logHandler, topicFilter=b""):

        self.logHandler = logHandler 

        if isinstance(addr, str):
           addr = addr.split(':')
           host, port = addr if len(addr) == 2 else (addr[0], None)

        self.host = host
        self.port = port

        self.context = zmq.asyncio.Context()
        loop = asyncio.get_event_loop()
        if isinstance(loop, zmq.asyncio.ZMQEventLoop):
            self.loop = loop
        else:
            self.loop = zmq.asyncio.ZMQEventLoop()
            asyncio.set_event_loop(self.loop)

        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind('tcp://%s:%s' % (self.host, self.port))
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topicFilter)


    def run(self):
        self.loop.create_task(self.handleLog())
        #self.loop.run_forever()

    async def handleLog(self):
        while True:
            level, message = await self.subscriber.recv_multipart()
            level = level.decode('ascii')
            message = message.decode('ascii')
            if message.endswith('\n'):
                # trim trailing newline, which will get appended again
                message = message[:-1]
                await self.logHandler(level + ': ' + message)
