# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 17:37:05 2015

@author: zech
"""


from simpleQuantConstants import *
from simpleQuantDecision import SimpleQuantDecision
from simpleQuantStrategy import SimpleQuantStrategyBase

class SimpleQuantStrategyFirstOne(SimpleQuantStrategyBase):
    def __init__(self):
        super().__init__()
        self.name = "strategyFirstOne"

    def getName(self):
        return self.name

    def tearUp(self):
        super().tearUp()

    def tearDown(self):
        super().tearDown()

    """
    currentObjectData: object data for the loop has following member:
                      date, open, close, price_change, p_change, low, high, volume, amount, turnover
    decisionList: decisions that the strategy made

    """

    def loop(self, currentObjectData, decisionList):
        close = currentObjectData.close
        decision = SimpleQuantDecision()
        if close < 12.30:
            decision.setAction(BID)
            decision.setVolumn(1000)
        elif close > 14.10:
            decision.setAction(ASK)
            decision.setVolumn(1000)

        return decision

