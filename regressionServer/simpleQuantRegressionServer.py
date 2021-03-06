import asyncio
import concurrent.futures
import logging
import json
import multiprocessing
import pandas as pd
import sys
#from zmq.utils import jsonapi as json

from common.simpleQuantZmqProcess import SimpleQuantZmqRequestReplyProcess
from common.simpleQuantLogger import SimpleQuantLogger
from simpleQuantStrategyManager import SimpleQuantStrategyManager
from simpleQuantDataManager import SimpleQuantDataManager
from simpleQuantTransition import SimpleQuantTransition

# Debug topic means system/framework log
logger = SimpleQuantLogger('Debug', '127.0.0.1:4321')

class SimpleQuantRegressionServerApplication(object):
    """ regression server application

    """
    def __init__(self, server, json_load=-1):
        self._json_load = json_load
        self.server = server
        self.server.registerMsg('getStrategyListReq', self.getStrategyListReq)
        self.server.registerMsg('connectionReq', self.connectionReq)
        self.server.registerMsg('getObjectDataReq', self.getObjectDataReq)
        self.server.registerMsg('startRegressionReq', self.startRegressionReq)
        self.server.registerMsg('getStrategySourceCodeReq', self.getStrategySourceCodeReq)
        self.server.registerMsg('getStretegyCustomizeParametersReq', self.getStretegyCustomizeParametersReq)
        self.strategyManager = SimpleQuantStrategyManager()
        self.dataManager = SimpleQuantDataManager()
        self.isConnected = False
        # Create a limited process pool.
        self.executor = concurrent.futures.ProcessPoolExecutor(
                            max_workers=multiprocessing.cpu_count(),
                        )

    async def connectionReq(self, msg):
        """
        received connect request message from client
        """
        #log = logging.getLogger('SimpleQuantRegressionServerApplication::connectionReq()')
        
        logger.info('client {name} connect.'.format(name=msg['name']))

        if False == self.isConnected:
            self.isConnected = True

        await self.server.send(['connectCfm', {'result': self.isConnected}])


    async def getStrategyListReq(self, msg):
        """
        client request strategy list
        """
        logger.info('client request strategy list.')
        id = 11
        strategyList = [{'name':strategyName, 'id':id} for id, strategyName in enumerate(self.strategyManager.getStrategyNameList())]
        logger.info("strategy list is {strategyList}".format(strategyList=strategyList))

        #get all strategy, make a list of them
        getStrategyListCfm = ['getStrategyListCfm', strategyList]
        #reply to client
        await self.server.send(getStrategyListCfm)
        logger.info('send out getStrategyListCfm')

    async def getStrategySourceCodeReq(self, msg):
        """
        client request strategy source code
        """
        logger.info('client request strategy source code.')
        strategyName = msg['strategyName']
        status, sourceCode = self.strategyManager.getStrategySourceCode(strategyName)
        if status != 0:
            respMsg = ['getStrategySourceCodeRej', {'status':status, 'msg':'Please check your strategy!'}]
        else:
            sourceCodeJson = json.dumps(sourceCode)
            respMsg = ['getStrategySourceCodeCfm', {'strategyName':strategyName, 'sourceCode':sourceCodeJson}]

        await self.server.send(respMsg)



    async def getStretegyCustomizeParametersReq(self, msg):
        """
        client request strategy customize parameters
        """
        logger.info('client request strategy customize parameter.')
        stretegyName = msg['strategyName']
        status, parametersList = self.strategyManager.getStretegyCustomizeParameters(stretegyName)
        if status != 0:
            respMsg = ['getStretegyCustomizeParametersRej', {'status':status, 'msg':'Please check your strategy!'}]
        else:
            respMsg = ['getStretegyCustomizeParametersCfm', parametersList]

        await self.server.send(respMsg)
        logger.info('send out getStretegyCustomizeParameters response.')

    async def getObjectDataReq(self, msg):
        """
        client request object data
        """
        logger.info('client request object Data.')

        objectName = msg['object']
        duration = msg['duration']
        logger.info('Request object {objectName} data.'.format(objectName=objectName))
        status, fetchedData = await self.dataManager.getObjectData(objectName, duration)

        if status != 0:
            sortedData = fetchedData.sort_values('date', ascending=True).reset_index(drop=True)
            respMsg = ['getObjectDataRej', {'status':status, 'msg':sortedData}]
        else:
            respMsg = ['getObjectDataCfm', fetchedData]

        await self.server.send(respMsg)

    async def startRegressionReq(self, msg):
        """
        client request start regression
        """
        logger.info('client request regression test')
        transitionJson = msg['transition']
        transitionDict = json.loads(transitionJson)

        transition = SimpleQuantTransition(transitionDict)
        await self.prepareTransition(transition)

        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(self.executor, transition)
        logger.info('waiting for executor task')

        objectData, report = await asyncio.wait_for(task, 60.0)


        respMsg = ['startRegressionCfm', {'objectData':objectData, 'report':report}]
        await self.server.send(respMsg)
        # get out the strategy name to be run

        # get out the strategy parameters

        # prepare for strategy

        # run strategy

        # return the result

    async def heartBeat(self, msg):
        """
        client check server alive or not
        """
        logger.info('client heart beat ')
        #reply heartBeatAck

    async def disconnectReq(self, msg):
        """
        client want close connection
        """
        logger.info('client close the connection')
        #

    async def prepareTransition(self, transition):
        objectName = transition.getTransitionObject()
        duration = transition.getTransitionDuration()
        status, fetchedData = await self.dataManager.getObjectData(objectName, duration) 
        if status == 0:
            df = pd.read_json(fetchedData)
            df = df.sort_values('date', ascending=True).reset_index(drop=True)
            transition.setTransitionObjectData(df)
        else:
            logger.info('prepare transition failed')
            return


class SimpleQuantRegressionServer(object):
    """ regression server
        
    """
    def __init__(self):
        logger.info('init simpleQuant regression server.')


    def start(self):
        """
        the server start running
        """
        #the server address has to be numeric, not DNS for zmq.bind
        #it's ok use DNS for zmq.connect
        self.serverAddr = '127.0.0.1:1234'
        self.serverProcess = SimpleQuantZmqRequestReplyProcess(True, self.serverAddr)
        self.serverApp = SimpleQuantRegressionServerApplication(self) 
        self.serverProcess.run()

    def stop(self):
        """
        stop the server 
        """
        self.serverProcess.stop()

    def registerMsg(self, msgName, msgHandler):
        self.serverProcess.registerMsg(msgName, msgHandler)

    async def send(self, msg):
        await self.serverProcess.send(msg)


