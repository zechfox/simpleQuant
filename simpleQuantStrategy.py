# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 21:30:02 2015

@author: zech
"""
from simpleQuantDataTweak import SimpleQuantDataTweak
import logging

MyLogger = logging.getLogger(__name__)   
class SimpleQuantStrategyBase:
    def __init__(self, dataManager):
        self.name = "strategyBase"
        self.data_tweak = SimpleQuantDataTweak()
        self.data_manager = dataManager
        self.history_data_size = 80
        
    def backTest(self):
        MyLogger.info("run back test, please wait")
        self.prepare();
        #loop for run()
        for index in range(self.backtest_windows_size):
            self.updateBackTestContext(index)
            self.run()
            self.profits.append(self.calculateCurrentProfit())
            
        MyLogger.info("Done!") 
        
        self.stop()
        
        return list(zip(self.data_manager.getStockDate(), self.profits[::-1]))
        
    def run(self):
        #this function will be called periodicaly in days for now
        #add your periodical strategy here
        #prepare data for strategy
        pass
    
    def prepare(self):
        self.current_flow = self.start_flow = 10000
        self.current_position = 0
        self.profits = []
        self.backtest_windows_size = self.data_manager.getCurrentDataSize()
        self.data_manager.initialHistoryWindow(self.history_data_size)
        self.data_manager.prepareHistoryData()
    
    def ask(self, percent = 100):
        self.current_flow = self.current_position * self.current_price * percent / 100
    
    def bid(self, percent = 100):
        self.current_position = self.current_flow * percent / (self.current_price * 100)
    
    def stop(self):
        #print(self.profits)
        pass
    
    def updateBackTestContext(self, index):
        self.data_manager.setHistoryDataStartIndex(index)
        lowPrice  = self.data_manager.getLowPrice()
        highPrice = self.data_manager.getHighPrice()
        self.current_price = (float(highPrice) + float(lowPrice)) / 2
        
    def calculateCurrentProfit(self):
        if self.current_position > 0:
            return (self.current_price * self.current_position - self.start_flow) / self.start_flow
        else:
            return (self.current_flow - self.start_flow) / self.start_flow
            
        
        