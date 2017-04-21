import aiohttp
import json
import os
import datetime

import pandas as pd

from .transitionDb import TransitionDb
from common.simpleQuantLogger import SimpleQuantLogger

from aiohttp import web

myLogger = SimpleQuantLogger(__name__, '127.0.0.1:4321')

async def index(request):
    return web.HTTPFound('/index.html')

async def transitions(request):
    respStatus = 404
    respData = 'Resource not found!'
    if request.method == 'POST':
        requestJson = await request.json()
        payloadJson = requestJson['payload']
        transitionJson = json.loads(payloadJson)
        transitionName = transitionJson['name']
        strategyName = transitionJson['strategyName']
        transitionObject = transitionJson['object']
        async with request.app['db'].acquire() as conn:
            newTransition = await TransitionDb.queryDbByName(conn, transitionName)
        if newTransition is None:
            newTransition = TransitionDb(transitionName, strategyName, transitionObject, '')
            if(newTransition.isParametersEmpty()):
                getStretegyCustomizeParametersReq = ['getStretegyCustomizeParametersReq', {'strategyName':strategyName}]
                await request.app['regressionClient'].send(getStretegyCustomizeParametersReq)
                respMsg = await request.app['regressionClient'].recv()
                msgName = respMsg[0]
                payload = respMsg[1]
                parameters = ''
                if msgName == 'getStretegyCustomizeParametersCfm':
                    parameters = json.dumps(payload)
                else:
                    myLogger.info('received getStretegyCustomizeParametersRej')
                newTransition.setCustomizeParameter(parameters)
            async with request.app['db'].acquire() as conn:
                await newTransition.insertDb(conn)
                transitionDict = newTransition.toDict()
                respData = transitionDict
                respStatus = 201
        else:
            myLogger.info('transition name already exist')
            respData = 'Transition Name already exist!'
            respStatus = 409

    elif request.method == 'GET':
        #get all transtions in the db
        async with request.app['db'].acquire() as conn:
            transitions = await TransitionDb.getAll(conn)
            if transitions:
                transitionsDict = [transition.toDict() for transition in transitions]
                respData = transitionsDict
                respStatus = 200
            else:
                respData = []
                respStatus = 200

    return web.json_response(respData, status=respStatus, dumps=json.dumps)

async def getStrategies(request):
    myLogger.info('recieve getStrategyListReq')
    respData = []
    respStatus = 200
    getStrategyListReq = ['getStrategyListReq', 1]
    await request.app['regressionClient'].send(getStrategyListReq)
    getStrategyListCfm =  await request.app['regressionClient'].recv()
    myLogger.info('recieve getStrategyListCfm')
    msgName = getStrategyListCfm[0]
    strategyList = getStrategyListCfm[1]
    if msgName == 'getStrategyListCfm':
        respData = strategyList

    return web.json_response(respData, status=respStatus)

async def getStrategyData(request):
    respStatus = 404
    respData = 'Resource not found!'
    name = request.match_info['name']
    data = request.match_info['data']

    if data == 'sourceCode':
        getStrategySourceCodeReq = ['getStrategySourceCodeReq', {'strategyName':name}]
        await request.app['regressionClient'].send(getStrategySourceCodeReq)
        respMsg = await request.app['regressionClient'].recv()
        msgName = respMsg[0]
        payload = respMsg[1]
        if msgName == 'getStrategySourceCodeCfm'\
            and name == payload['strategyName']:
            respData = json.loads(payload['sourceCode'])
            respStatus = 200

    resp = web.json_response(respData, status=respStatus)
    return resp

async def getTransitionData(request):
   transitionId = request.match_info['transitionId']
   data = request.match_info['data']
   regressionClient = request.app['regressionClient']
   async with request.app['db'].acquire() as conn:
       transition = await TransitionDb.queryDbById(conn, transitionId)
   respStatus = 404
   respData = 'Resource not found!'
  
   if request.method == 'GET' \
        and (transition is not None):
        if data == 'objectData':
            getObjectDataReq = ['getObjectDataReq', { 'object':transition.object, 'duration':transition.duration }]
            await regressionClient.send(getObjectDataReq)
            respMsg = await regressionClient.recv()
            msgName = respMsg[0]
            payload = respMsg[1]
            if msgName == 'getObjectDataCfm':
                myLogger.info('receive getObjectDataCfm')
                df = pd.read_json(payload)
                df.sort_index(inplace=True, ascending=True)
                dataSets = [{'data':(df['close'].values.tolist()), 'label':'close'}]
                labels = df['date'].apply(lambda x: x.strftime('%Y%m%d')).values.tolist()
                results = [{'data': [0] * len(labels), 'label':'Market Value'}]
                report = []

                respData = {'objectName':transition.object, 'dataSets':dataSets, 'labels':labels, 'results': results, 'evaluateReport':report}
                respStatus = 200
            elif msgName == 'getObjectDataRej':
                myLogger.info('receive getObjectDataRej with status:{status}, message:{message}.'.format(status=payload['status'], message=payload['msg']))
               
                respData = payload
                respStatus = 404 
            else:
                myLogger.info('received unexpect message:{msgName}'.format(msgName=msgName))
        elif data == 'results':
            startRegressionReq = ['startRegressionReq', { 'transition':transition.toJSON() }]
            await regressionClient.send(startRegressionReq)
            respMsg = await regressionClient.recv()
            msgName = respMsg[0]
            payload = respMsg[1]
            objectData = payload['objectData']
            report = json.loads(payload['report'])
            reportList = [{'name':k,'value':v} for (k, v) in report.items()]
            if msgName == 'startRegressionCfm':
                myLogger.info('receive startRegressionCfm')
                df = pd.read_json(objectData)
                df.sort_index(inplace=True, ascending=True)
                results = [{'data':(df['marketValue'].values.tolist()), 'label':'Market Value'}]
                labels = df['date'].apply(lambda x: x.strftime('%Y%m%d')).values.tolist()
                dataSets = [{'data':(df['close'].values.tolist()), 'label':'close'}]
                #results = [{'data':[0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'label':'Market Value'}]
                #labels = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13'];
                #dataSets = results
                respData = {'objectName':transition.object, 'dataSets':dataSets, 'labels':labels, 'results': results, 'evaluateReport': reportList}
                respStatus = 200
            elif msgName == 'startRegressionRej':
                myLogger.info('receive startRegressionRej with status:{status}, message:{message}.'.format(status=payload['status'], message=payload['msg']))
               
                respData = payload
                respStatus = 404 

   return web.json_response(respData, status=respStatus)

async def updateTransition(request):
   transitionId = request.match_info['transitionId'] 
   regressionClient = request.app['regressionClient']
   async with request.app['db'].acquire() as conn:
       transition = await TransitionDb.queryDbById(conn, transitionId)
   respStatus = 404
   respData = 'Resource not found!'
   if request.method == 'POST':
      if transition is None:
          #error here
          pass
               
      #update transtion information
      else:
          requestJson = await request.json()
          payloadJson = requestJson['payload']
          transitionDict = json.loads(payloadJson)
          #TODO: validate name, strategyName, object, duration
          transition.updateFromDict(transitionDict)

          #update customize parameters if needed
          if(transition.isParametersEmpty()):
              getStretegyCustomizeParametersReq = ['getStretegyCustomizeParametersReq', {'strategyName':transition.strategyName}]
              await regressionClient.send(getStretegyCustomizeParametersReq)
              respMsg = await regressionClient.recv()
              msgName = respMsg[0]
              payload = respMsg[1]
              parameters = ''
              if msgName == 'getStretegyCustomizeParametersCfm':
                  parameters = json.dumps(payload)
              else:
                  myLogger.info('received getStretegyCustomizeParametersRej')

              myLogger.info(type(parameters))
              myLogger.info(parameters)
              transition.setCustomizeParameter(parameters)

          async with request.app['db'].acquire() as conn:
              await transition.updateDb(conn)
          respData = transition.toDict()
          respStatus = 200

   return web.json_response(respData, status=respStatus)

async def websocketHandler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            wsData = json.loads(msg.data)
            id = wsData['id']
            message = wsData['message']
            if message == 'disconnect':
                await ws.close(code=1001, message='Server shutdown')
                del request.app['websockets'][id]
                return ws
            elif message == 'connect':
                request.app['websockets'][id] = ws



