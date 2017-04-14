# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 17:37:05 2015

@author: zech
"""
from common.simpleQuantLogger import SimpleQuantLogger
from simpleQuantConstants import *
from simpleQuantDecision import SimpleQuantDecision
from simpleQuantStrategy import SimpleQuantStrategyBase


customizeParameterList = [{'name': 'DEA', 'value': ''},\
                          {'name': 'DIF', 'value': ''},\
                          {'name': 'EmaFast', 'value': ''},\
                          {'name': 'EmaSlow', 'value': ''}]

class SimpleQuantStrategyMACD(SimpleQuantStrategyBase):
    def __init__(self):
        super().__init__()
        self.name = 'strategyMACD'
        self.lastDEA = 0  #DEA is mea(DIF, 9)
        self.lastDIF = 0
        self.lastEmaFast = 0 # ema fast is mea(close, 12)
        self.lastEmaSlow = 0 # ema slow is mea(close, 26)
    
    def tearUP(self):
        super().tearUP()
        self.lastDIF = 14.21
        self.lastEmaFast = 14.21
        self.lastEmaSlow = 12.54
    
    def tearDown(self):
        super().tearDown()
    
    def mea(self, new, old, duration):
        alpha = 2/(duration + 1)
        beta = 1 - alpha
        return new * alpha + beta * old
    
    
    def loop(self, objectData, decisionList):
        close = objectData.close
        decision = SimpleQuantDecision()
        newEmaFast = self.mea(close, self.lastEmaFast, 12)
        newEmaSlow = self.mea(close, self.lastEmaSlow, 26)
        newDIF = newEmaFast - newEmaSlow
        newDEA = self.mea(newDIF, self.lastDEA, 9)
    
        if (self.lastDIF < self.lastDEA) \
            and (newDIF > newDEA):
            decision.setAction(BID)
            decision.setVolumn(1000)
      
        if (self.lastDIF > self.lastDEA) \
            and (newDIF < newDEA):
            decision.setAction(ASK)
            decision.setVolumn(1000)
    
    
        self.lastEmaSlow = newEmaSlow
        self.lastEmaFast = newEmaFast
        self.lastDEA = newDEA
        self.lastDIF = newDIF
    
        return decision
