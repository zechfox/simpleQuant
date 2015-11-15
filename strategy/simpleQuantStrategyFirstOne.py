# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 17:37:05 2015

@author: zech
"""

from simpleQuantStrategy import SimpleQuantStrategyBase

class SimpleQuantStrategyFirstOne(SimpleQuantStrategyBase):
    def __init__(self, dataManager):
        super().__init__(dataManager)
        self.name = "strategyFirstOne"

    def run(self):
        #this function will be called periodicaly in days for now
        #add your periodical strategy here
        #prepare data for strategy
        historyPrice = list(map(float, self.data_manager.getHistoryStockData()))     
        signal, hist, macd = self.data_tweak.movingAverageConvergence(historyPrice)

        if ((macd[-1] - signal[-1]) < 0) and ((macd[-2] - signal[-2]) > 0):     
            if self.current_position > 0:    
                self.ask()
                
        if (macd[-1] - signal[-1]) > 0 and (macd[-2] - signal[-2]) < 0:
            self.bid()