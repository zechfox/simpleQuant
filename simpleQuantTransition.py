# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 16:11:44 2016

@author: zech
"""
import datetime
import logging
import json

from simpleQuantDataManager import SimpleQuantUIDataManager
from simpleQuantEventEngine import SimpleQuantEventEngine
from simpleQuantStrategyManager import SimpleQuantStrategyManager
from simpleQuantSafeProcess import SimpleQuantSafeProcess


MyLogger = logging.getLogger(__name__)

class SimpleQuantTransition(SimpleQuantSafeProcess):
    def __init__(self, stockSymbol, strategyName, startDate, endDate, feedbackQueue):
        SimpleQuantSafeProcess.__init__(self, feedbackQueue)
        self.strategy_manager = SimpleQuantStrategyManager()
        self.data_manager = SimpleQuantUIDataManager(stockSymbol, startDate, endDate)
        self.event_engine = SimpleQuantEventEngine()
        self.strategy_name = strategyName

    def getStockData(self):
        hqData = self.data_manager.getStockData()
        return hqData

    #TODO: remove runStrategy() when multi-process done
    def runStrategy(self, strategyName):
        MyLogger.info("Run Strategy")
        self.strategy_manager.setStrategyName(strategyName)
        self.stock_strategy = self.strategy_manager.getStrategyInstance()(self.data_manager)
        self.profitsData = self.stock_strategy.backTest()
        return self.profitsData

    def updateTransitionContext(self, startDate, endDate):
        self.data_manager.setStockContext(startDate, endDate)

    def getStrategyNameList(self):
        return self.strategy_manager.getStrategyNameList()

    def saferun(self):
        MyLogger.info("Start Transition")
        MyLogger.info("Run Strategy")
        self.strategy_manager.setStrategyName(self.strategy_name)
        self.stock_strategy = self.strategy_manager.getStrategyInstance()(self.data_manager)
        self.profitsData = self.stock_strategy.backTest()
        self.endUp()

    def endUp(self):
        MyLogger.info("End Up Transition")
        hqData = self.getStockData()
        profits = self.profitsData
        with open('app/static/json/hqData.json', 'w') as f:
            f.write(json.dumps(hqData))
        with open('app/static/json/profits.json', 'w') as f:
            f.write(json.dumps(profits))
