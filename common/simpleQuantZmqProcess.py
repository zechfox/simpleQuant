# simpleQuantZmqProcess.py 
# all zmq processes can be get from here

import asyncio
import zmq.asyncio
import zmq
import time
from zmq.utils import jsonapi as json

from zmq.eventloop import ioloop, zmqstream


class SimpleQuantZmqProcessBase():
    """
    This is the base for all zmq processes and offers utility functions
    for setup and creating new streams.

    """
    def __init__(self):
        super().__init__()

        self.context = None
        """The ØMQ :class:`~zmq.Context` instance."""

        self.loop = None
        """PyZMQ's event loop (:class:`~zmq.eventloop.ioloop.IOLoop`)."""

    def setup(self, sock_type, addr, bind, subscribe=b''):
        """
        Creates a :attr:`context` and an event :attr:`loop` for the process.

        """
        self.context = zmq.asyncio.Context()
        self.loop = zmq.asyncio.ZMQEventLoop()
        asyncio.set_event_loop(self.loop)

        sock = self.context.socket(sock_type)

        # addr may be 'host:port' or ('host', port)
        if isinstance(addr, str):
            addr = addr.split(':')
            host, port = addr if len(addr) == 2 else (addr[0], None)


        # Bind/connect the socket
        if bind:
            if port:
                sock.bind('tcp://%s:%s' % (host, port))
            else:
                port = sock.bind_to_random_port('tcp://%s' % host)
        else:
                sock.connect('tcp://%s:%s' % (host, port))

        # Add a default subscription for SUB sockets
        if sock_type == zmq.SUB:
            sock.setsockopt(zmq.SUBSCRIBE, subscribe)

        self.sock = sock

    def stream(self, sock_type, addr, bind, callback=None, subscribe=b''):
        """
        Creates a :class:`~zmq.eventloop.zmqstream.ZMQStream`.

        :param sock_type: The ØMQ socket type (e.g. ``zmq.REQ``)
        :param addr: Address to bind or connect to formatted as *host:port*,
                *(host, port)* or *host* (bind to random port).
                If *bind* is ``True``, *host* may be:

                - the wild-card ``*``, meaning all available interfaces,
                - the primary IPv4 address assigned to the interface, in its
                numeric representation or
                - the interface name as defined by the operating system.

                If *bind* is ``False``, *host* may be:

                - the DNS name of the peer or
                - the IPv4 address of the peer, in its numeric representation.

                If *addr* is just a host name without a port and *bind* is
                ``True``, the socket will be bound to a random port.
        :param bind: Binds to *addr* if ``True`` or tries to connect to it
                otherwise.
        :param callback: A callback for
                :meth:`~zmq.eventloop.zmqstream.ZMQStream.on_recv`, optional
        :param subscribe: Subscription pattern for *SUB* sockets, optional,
                defaults to ``b''``.
        :returns: A tuple containg the stream and the port number.

        """
        sock = self.context.socket(sock_type)

        # addr may be 'host:port' or ('host', port)
        if isinstance(addr, str):
            addr = addr.split(':')
            host, port = addr if len(addr) == 2 else (addr[0], None)


        # Bind/connect the socket
        if bind:
            if port:
                sock.bind('tcp://%s:%s' % (host, port))
            else:
                port = sock.bind_to_random_port('tcp://%s' % host)
        else:
                sock.connect('tcp://%s:%s' % (host, port))

        # Add a default subscription for SUB sockets
        if sock_type == zmq.SUB:
            sock.setsockopt(zmq.SUBSCRIBE, subscribe)
        # Create the stream and add the callback
        stream = zmqstream.ZMQStream(sock, self.loop)
        if callback:
            stream.on_recv(callback)

        return stream, int(port)

class SimpleQuantZmqRequestReplyProcess(SimpleQuantZmqProcessBase):
    """server/client process for request-response model

    """
    def __init__(self, isServer, bind_addr):
        super().__init__()

        self.bind_addr = bind_addr
        self.rep_stream = None
        self.socketType = zmq.REP if isServer else zmq.REQ
        self.isServer = isServer
        self._json_load = -1
        self.msg_table = {}
        self.status = 'not running'

    def setup(self):
        """
        setup zmq and create stream for Request 
        """
        super().setup(self.socketType, self.bind_addr, bind=self.isServer)
        """ Create the stream and add the message handler """
        #self.rep_stream, _ = self.stream(self.socketType, self.bind_addr, bind=self.isServer, callback=self.messageHandler)

        
    def run(self):
        """Sets up everything and starts the event loop."""
        self.setup()
        if self.isServer:
            self.loop.create_task(self.messageHandler())
            self.loop.run_forever()
          

    def stop(self):
        """Stops the event loop."""
        self.loop.stop()

    async def send(self, obj):
        msg = json.dumps(obj) 
        await self.sock.send(msg)

    async def recv(self):
        msg = await self.sock.recv_multipart()
        return json.loads(msg[0])

    def registerMsg(self, msgName, msgHandler):
        self.msg_table.update({msgName:msgHandler})

    async def messageHandler(self):
        """
        Gets called when a messages is received by the stream this handlers is
        registered at. *msg* is a list as return by
        :meth:`zmq.core.socket.Socket.recv_multipart`.
        """
        while True:
            msg = await self.sock.recv_multipart()

            # Try to JSON-decode the index "self._json_load" of the message
            print("messageHandler() receive message!")
            i = self._json_load
            msgName, data = json.loads(msg[i])
            msg[i] = data
            # Get the actual message handler and call it
            if msgName.startswith('_'):
                raise AttributeError('%s starts with an "_"' % msgName)
            if msgName in self.msg_table:
                self.loop.create_task(self.msg_table[msgName](*msg))

