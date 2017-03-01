import os

from zmq.utils import jsonapi as json

from common.simpleQuantZmqProcess import SimpleQuantZmqRequestReplyProcess

class SimpleQuantRegressionClientApplication(object):
    """ regression server application

    """
    def __init__(self, client, json_load=-1):
        self._json_load = json_load

    def __call__(self, msg):
        """
        Gets called when a messages is received by the stream this handlers is
        registered at. *msg* is a list as return by
        :meth:`zmq.core.socket.Socket.recv_multipart`.

        """
        # Try to JSON-decode the index "self._json_load" of the message
        i = self._json_load
        msg_type, data = json.loads(msg[i])
        msg[i] = data

        # Get the actual message handler and call it
        if msg_type.startswith('_'):
            raise AttributeError('%s starts with an "_"' % msg_type)

        getattr(self, msg_type)(*msg)

    def connectCfm(self, msg):
        """
        received connect confirm message from server 
        """
        print('server {name} connect.'.format(name=msg['name']))

        if False == self.isConnected:
            self.isConnected = True

        self.server.send(['connectCfm', {'result': self.isConnected}])


    def getStrategyListReq(self, msg):
        """
        client request strategy list
        """
        print('client request strategy list.')

        #get all strategy, make a list of them

        #reply to client

    def startRegressionReq(self, msg):
        """
        client request start regression
        """
        print('client request regression test')

        #get out the strategy name to be run

        #get out the strategy parameters

        #prepare for strategy

        #run strategy

        #return the result

    def heartBeat(self, msg):
        """
        client check server alive or not
        """
        print('client heart beat ')
        #reply heartBeatAck

    def disconnectReq(self, msg):
        """
        client want close connection
        """
        print('client close the connection')
        #



class SimpleQuantRegressionServer(object):
    """ regression server
        
    """
    def __init__(self):
        print('init')


    def start(self):
        """
        the server start running
        """
        self.serverAddr = 'localhost:1234'

        self.serverApp = SimpleQuantRegressionSeverApplication(this) 
        self.serverProcess = SimpleQuantZmqRequestReplyProcess(True, self.serverAddr, self.serverApp)
        self.serverProcess.run()

    def stop(self):
        """
        stop the server 
        """
        self.serverProcess.stop()



def main():
    server = SimpleQuantRegressionServer()
    server.start()


if __name__ == '__main__':
    main()
