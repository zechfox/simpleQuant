# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:40:08 2015

@author: zech
"""
import json
import os
import datetime
import time
from multiprocessing import Queue
from flask import request, send_from_directory, flash, url_for, session
from flask import Response
import pandas as pd
import zmq

from app import app, db
from app.transition import Transition
 
#from zmq.utils import jsonapi as json

from common.simpleQuantZmqProcess import SimpleQuantZmqRequestReplyProcess

feedback_queue = Queue()

serverAddr = '127.0.0.1:1234'
regressionClient = SimpleQuantZmqRequestReplyProcess(False, serverAddr)
regressionClient.run()
msg = ['connectionReq', {'name':'zechfox'}]
context = zmq.Context()
sock = context.socket(zmq.REQ)
sock.connect('tcp://%s:%s' % ('127.0.0.1', 1234))
sock.send_json(msg)
connectionCfm = sock.recv_json()

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file("index.html")

@app.route('/transitions', methods=['GET','POST'])
def transitions():
    if request.method == 'POST':
        requestJson = request.get_json()
        payloadJson = requestJson['payload']
        transitionJson = json.loads(payloadJson)
        transitionName = transitionJson['name']
        strategyName = transitionJson['strategyName']
        transitionObject = transitionJson['object']
        newTransition = Transition.query.filter_by(name=transitionName).first()
        if newTransition is None:
            newTransition = Transition(transitionName, strategyName, transitionObject)
            if(newTransition.isParametersEmpty()):
                getStretegyCustomizeParametersReq = ['getStretegyCustomizeParametersReq', {'strategyName':strategyName}]
                sock.send_json(getStretegyCustomizeParametersReq)
                respMsg = sock.recv_json()
                msgName = respMsg[0]
                payload = respMsg[1]
                parameters = ''
                if msgName == 'getStretegyCustomizeParametersCfm':
                    parameters = json.dumps(payload)
                    print(parameters)
                else:
                    print('received getStretegyCustomizeParametersRej')

                newTransition.setCustomizeParameter(parameters)
            db.session.add(newTransition)
            db.session.commit()
            transitionJson = newTransition.toJSON()

            resp = Response(transitionJson, status=201, mimetype='application/json')
        else:
            print('transition name already exist')
            resp = Response(json.dumps('Transition Name already exist!'), status=409, mimetype='application/json')

    elif request.method == 'GET':
        #get all transtions in the db
        transitions =  Transition.query.all()
        transitionsDict = [transition.toDict() for transition in transitions]
        transitionsJson = json.dumps(transitionsDict)
        resp = Response(transitionsJson, status=200, mimetype='application/json')

    return resp


@app.route('/transition', methods=['GET','POST'])
def transition():
    #TODO: run strategy in new process
    #1. start transition in new process
    #2. display page as well. wait until transition finish. It's no need render template instantly after strat transtion,
    #   because javascript can display page as well when click 'start strategy', while in backend, parent process wait for
    #   transition process finish, then render the template again, the well will disapear.
    #3. render the template
    #wait transition finish
    print('can route to transition')
    return 'index'

@app.route('/manageStrategy', methods=['GET','POST'])
@app.route('/manageStrategy/<string:page>', methods=['GET','POST'])
def manageStrategy(page = ''):
    #1. check page is valid or not, if page not empty
    #2. if page = '' or not valid, list all strategy name
    #3. if page = valid strategy name, render strategy editor with preload strategy code
    #4. if page = 'newStrategy', render strategy editor with preload strategy template code
    return
@app.route('/strategies', methods=['GET'])
def getStrategies():
    print('recieve getStrategyListReq')
    getStrategyListReq = ['getStrategyListReq', 1]
    sock.send_json(getStrategyListReq)
    getStrategyListCfm = sock.recv_json()
    print('recieve getStrategyListCfm')
    msgName = getStrategyListCfm[0]
    strategyList = getStrategyListCfm[1]
    if msgName == 'getStrategyListCfm':
        strategyList_json = json.dumps(strategyList)
        resp = Response(strategyList_json, status=200, mimetype='application/json')
        return resp

    print('received wrong msge')

@app.route('/strategy/detail/<string:name>/<string:data>', methods=['GET'])
def getStrategyData(name, data):
    respStatus = 404
    respData = 'Resource not found!'

    if data == 'sourceCode':
        getStrategySourceCodeReq = ['getStrategySourceCodeReq', {'strategyName':name}]
        sock.send_json(getStrategySourceCodeReq)
        print('send out getStrategySourceCodeReq')
        respMsg = sock.recv_json()
        msgName = respMsg[0]
        payload = respMsg[1]
        print('received getStrategySourceCodeReq response, msgName:{msgName}'.format(msgName=msgName))
        if msgName == 'getStrategySourceCodeCfm'\
            and name == payload['strategyName']:
            print('strategyname:name'.format(name=name))
            respData = payload['sourceCode']
            respStatus = 200

    resp = Response(respData, status=respStatus, mimetype='application/json')
    return resp



@app.route('/transition/detail/<int:transitionId>/<string:data>', methods=['GET'])
def getTransitionData(transitionId, data):
   transition = Transition.query.filter_by(id=transitionId).first()
   respStatus = 404
   respData = 'Resource not found!'
  
   if request.method == 'GET' \
        and (transition is not None):
        if data == 'objectData':
            getObjectDataReq = ['getObjectDataReq', { 'object':transition.object, 'duration':transition.duration }]
            sock.send_json(getObjectDataReq)
            respMsg = sock.recv_json()
            msgName = respMsg[0]
            payload = respMsg[1]
            if msgName == 'getObjectDataCfm':
                print('receive getObjectDataCfm')
                df = pd.read_json(payload)
                df.sort_index(inplace=True, ascending=False)
                dataSets = [{'data':(df['close'].values.tolist()), 'label':'close'}]
                labels = df['date'].apply(lambda x: x.strftime('%Y%m%d')).values.tolist()
                results = [{'data': [0] * len(labels), 'label':'Market Value'}]
                report = []

                respData = {'objectName':transition.object, 'dataSets':dataSets, 'labels':labels, 'results': results, 'evaluateReport':report}
                respStatus = 200
            elif msgName == 'getObjectDataRej':
                print('receive getObjectDataRej with status:{status}, message:{message}.'.format(status=payload['status'], message=payload['msg']))
               
                respData = payload
                respStatus = 404 
            else:
                print('received unexpect message:{msgName}'.format(msgName=msgName))
        elif data == 'results':
            startRegressionReq = ['startRegressionReq', { 'transition':transition.toJSON() }]
            sock.send_json(startRegressionReq)
            respMsg = sock.recv_json()
            msgName = respMsg[0]
            payload = respMsg[1]
            objectData = payload['objectData']
            report = json.loads(payload['report'])
            reportList = [{'name':k,'value':v} for (k, v) in report.items()]
            if msgName == 'startRegressionCfm':
                print('receive startRegressionCfm')
                df = pd.read_json(objectData)
                df.sort_index(inplace=True, ascending=False)
                results = [{'data':(df['marketValue'].values.tolist()), 'label':'Market Value'}]
                labels = df['date'].apply(lambda x: x.strftime('%Y%m%d')).values.tolist()
                dataSets = [{'data':(df['close'].values.tolist()), 'label':'close'}]
                #results = [{'data':[0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'label':'Market Value'}]
                #labels = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13'];
                #dataSets = results
                respData = {'objectName':transition.object, 'dataSets':dataSets, 'labels':labels, 'results': results, 'evaluateReport': reportList}
                respStatus = 200
            elif msgName == 'startRegressionRej':
                print('receive startRegressionRej with status:{status}, message:{message}.'.format(status=payload['status'], message=payload['msg']))
               
                respData = payload
                respStatus = 404 

   respJsonData = json.dumps(respData)
   return Response(respJsonData, status=respStatus, mimetype='application/json')


@app.route('/transition/detail/<int:transitionId>', methods=['POST'])
def updateTransition(transitionId):
   transition = Transition.query.filter_by(id=transitionId).first()
   resp = Response(status=404, mimetype='application/json')
   if request.method == 'POST':
      if transition is None:
          #error here
          pass
               
      #update transtion information
      else:
          requestJson = request.get_json()
          payloadJson = requestJson['payload']
          transitionDict = json.loads(payloadJson)
          #TODO: validate name, strategyName, object, duration
          transition.updateFromDict(transitionDict)

          #update customize parameters if needed
          if(transition.isParametersEmpty()):
              getStretegyCustomizeParametersReq = ['getStretegyCustomizeParametersReq', {'strategyName':transition.strategyName}]
              sock.send_json(getStretegyCustomizeParametersReq)
              respMsg = sock.recv_json()
              msgName = respMsg[0]
              payload = respMsg[1]
              parameters = ''
              if msgName == 'getStretegyCustomizeParametersCfm':
                  parameters = json.dumps(payload)
              else:
                  print('received getStretegyCustomizeParametersRej')

              transition.setCustomizeParameter(parameters)

          db.session.commit()
          transitionJson = transition.toJSON()

          resp = Response(transitionJson, status=200, mimetype='application/json')


   return resp
