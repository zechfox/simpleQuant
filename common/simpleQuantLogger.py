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

from zmq.utils.strtypes import bytes, unicode, cast_bytes


TOPIC_DELIM="::" # delimiter for splitting topics on the receiving end.

class SimpleQuantLogPublisher(logging.Handler):
    """
     a basic logging handler that copy from zmq PUBHandler
     changed the log format
    """
    formatters = {
        logging.DEBUG: logging.Formatter(
            "%(asctime)s  DEBUG: %(levelname)s %(filename)s:%(lineno)d - %(message)s\n"),
        logging.INFO: logging.Formatter("%(asctime)s  INFO: %(message)s\n"),
        logging.WARN: logging.Formatter(
            "%(asctime)s  WARN: %(levelname)s %(filename)s:%(lineno)d - %(message)s\n"),
        logging.ERROR: logging.Formatter(
            "%(asctime)s  ERROR: %(levelname)s %(filename)s:%(lineno)d - %(message)s - %(exc_info)s\n"),
        logging.CRITICAL: logging.Formatter(
            "%(asctime)s  CRITICAL: %(levelname)s %(filename)s:%(lineno)d - %(message)s\n")}

    def __init__(self, interface_or_socket, context=None):
        logging.Handler.__init__(self)
        if isinstance(interface_or_socket, zmq.Socket):
            self.socket = interface_or_socket
            self.ctx = self.socket.context
        else:
            self.ctx = context or zmq.Context()
            self.socket = self.ctx.socket(zmq.PUB)
            self.socket.bind(interface_or_socket)

    def format(self,record):
        """Format a record."""
        return self.formatters[record.levelno].format(record)

    def emit(self, record):
        """Emit a log message on my socket."""
        try:
            topic, record.msg = record.msg.split(TOPIC_DELIM,1)
        except Exception:
            topic = ""
        try:
            bmsg = cast_bytes(self.format(record))
        except Exception:
            self.handleError(record)
            return
        
        if isinstance(topic, str):
            btopic = cast_bytes(topic)
        else:
            print("Exception: topic is not string:{topic}".format(topic=topic))
            btopic = b'Debug' 

        self.socket.send_multipart([btopic, bmsg])



class SimpleQuantLogger(logging.Logger):
    def __init__(self, topic, loggerServerAddr):

        super().__init__(topic)
        self.name = topic

        if isinstance(loggerServerAddr, str):
            addr = loggerServerAddr.split(':')
            host, port = addr if len(addr) == 2 else (addr[0], None)
        self.loggerServerHost = host
        self.loggerServerPort = port

        context = zmq.asyncio.Context()

        publisher = context.socket(zmq.PUB)
        publisher.connect('tcp://%s:%s' %(self.loggerServerHost, self.loggerServerPort))
        handler = SimpleQuantLogPublisher(publisher)
        handler.root_topic = topic
        self.addHandler(handler)
        for name in "debug warn warning error critical fatal info".split():
            meth = getattr(logging.Logger,name)
            setattr(SimpleQuantLogger, name, 
                    lambda self, msg, *args, **kwargs: 
                        meth(self, topic+TOPIC_DELIM+msg,*args, **kwargs))

    def log(self, level, msg, *args, **kwargs):
        """Log 'msg % args' with level and topic.
        To pass exception information, use the keyword argument exc_info
        with a True value::
        logger.log(level, "We have a %s", 
                "mysterious problem", exc_info=1)
        """
        logging.Logger.log(self, level, '%s::%s'%(self.name, msg), *args, **kwargs)


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
            topic, message = await self.subscriber.recv_multipart()
            topic = topic.decode('ascii')
            message = message.decode('ascii')
            if message.endswith('\n'):
                # trim trailing newline, which will get appended again
                message = message[:-1]
                await self.logHandler(topic, message)
