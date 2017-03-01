import unittest
import unittest.mock as mock
import zmq

from zmq.eventloop import ioloop, zmqstream

#my modules
from common.simpleQuantZmqProcess import SimpleQuantZmqProcessBase
from common.simpleQuantZmqProcess import SimpleQuantZmqRequestReplyProcess

class TestZmqProcessBase(unittest.TestCase):
    def setUp(self):
        """
        prepare work for test
        """
    def tearDown(self):
        """
        clean up for test
        """
    def test_setup(self):
        """
        test for setup function
        """
        zp = SimpleQuantZmqProcessBase()
        zp.setup()
        self.assertIsInstance(zp.context, zmq.Context)
        self.assertIsInstance(zp.loop, ioloop.IOLoop)

    def test_stream(self):
        """
        testcase for stream function 
        """
        zp = SimpleQuantZmqProcessBase()
        # Patch the ZmqProcess instance
        zp.context = mock.Mock(spec_set=zmq.Context)
        zp.loop = mock.Mock(spec_set=ioloop.IOLoop)
        sock_mock = zp.context.socket.return_value
        sock_mock.bind_to_random_port.return_value = 42
        
        kwargs = dict(sock_type=zmq.REP, addr='127.0.0.1:1234', bind=True,callback=mock.Mock())


        # Patch ZMQStream and start testing
        with mock.patch('zmq.eventloop.zmqstream.ZMQStream') as zmqstream_mock:
            stream, port = zp.stream(**kwargs)
            self.assertIs(stream, zmqstream_mock.return_value)
            self.assertEqual(port, int(kwargs['addr'][-4:]))
            self.assertEqual(zp.context.socket.call_args, mock.call(kwargs['sock_type']))
            self.assertEqual(sock_mock.bind.call_args, mock.call(('tcp://%s' % kwargs['addr'])))
            self.assertEqual(zmqstream_mock.call_args, mock.call(sock_mock, zp.loop))

    def runAll(self):
        unittest.main()

class TestZmqRequestReplyProcess(unittest.TestCase):
    def setUp(self):
        """
        prepare work for test
        """
    def tearDown(self):
        """
        clean up for test
        """
    def test_ServerSetup(self):
        """
        test for setup function
        """
        kwargs = dict(isServer=True, bind_addr='127.0.0.1:1234')
        zp = SimpleQuantZmqRequestReplyProcess(**kwargs)
        zp.context = mock.Mock(spec_set=zmq.Context)
        zp.loop = mock.Mock(spec_set=ioloop.IOLoop)
        sock_mock = zp.context.socket.return_value
        sock_mock.bind_to_random_port.return_value = 42

        with mock.patch('zmq.eventloop.zmqstream.ZMQStream') as zmqstream_mock:
            zp.setup()
            self.assertIs(zp.rep_stream, zmqstream_mock.return_value)
            self.assertEqual(zp.rep_stream.on_recv.call_args, mock.call(zp.messageHandler))

    def test_ClientSetup(self):
        """
        test for setup function
        """
        kwargs = dict(isServer=False, bind_addr='127.0.0.1:1234')
        zp = SimpleQuantZmqRequestReplyProcess(**kwargs)
        zp.context = mock.Mock(spec_set=zmq.Context)
        zp.loop = mock.Mock(spec_set=ioloop.IOLoop)
        sock_mock = zp.context.socket.return_value
        sock_mock.bind_to_random_port.return_value = 42

        with mock.patch('zmq.eventloop.zmqstream.ZMQStream') as zmqstream_mock:
            zp.setup()
            self.assertIs(zp.rep_stream, zmqstream_mock.return_value)
            self.assertEqual(zp.rep_stream.on_recv.call_args, mock.call(zp.messageHandler))


    def runAll(self):
        unittest.main()


if __name__ == '__main__':
    unittest.main()
