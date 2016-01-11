# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 16:11:44 2016

@author: zech
"""
import datetime

from simpleQuantDataManager import SimpleQuantUIDataManager
from simpleQuantEventEngine import SimpleQuantEventEngine
from simpleQuantStrategyManager import SimpleQuantStrategyManager

class SimpleQuantTransition():
    def __init__(self, stockSymbol):
        endDate = datetime.datetime.today()
        deltaDays = datetime.timedelta(days=-60)
        startDate = endDate + deltaDays
        self.strategy_manager = SimpleQuantStrategyManager()
        self.data_manager = SimpleQuantUIDataManager(stockSymbol, startDate, endDate)
        self.event_engine = SimpleQuantEventEngine()
    
    def getStockData(self):
        hqData = self.data_manager.getStockData()
        return hqData
    
    def runStrategy(self):
        #temp manually
        strategyName = "simpleQuantStrategyMACD"
        self.strategy_manager.setStrategyName(strategyName)
        
        self.stock_strategy = self.strategy_manager.getStrategyInstance()(self.data_manager)
        profitsData = self.stock_strategy.backTest()
        
        return profitsData
        
    def updateTransitionContext(self, startDate, endDate):
        self.data_manager.setStockContext(startDate, endDate)