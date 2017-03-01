import json
import logging
import pandas as pd
import sys

from simpleQuantConstants import *
from simpleQuantStrategyManager import SimpleQuantStrategyManager

class SimpleQuantTransition:
    def __init__(self, jsonString):
        self.name = jsonString['name']
        self.strategyName = jsonString['strategyName']
        self.object = jsonString['object']
        self.duration = jsonString['duration']
        self.objectData = pd.DataFrame()
        self.strategy = SimpleQuantStrategyManager().getStrategyInstance(self.strategyName)()
        self.loopIndex = 0

        self.cashHistory= []
        self.positionHistory = []
        self.marketValue = []

        logging.basicConfig(
            level=logging.INFO,
            format='PID %(process)5s %(name)18s: %(message)s',
            stream=sys.stderr,
        )


    def __call__(self):
        log = logging.getLogger('SimpleQuantTransition')
        log.info('{name} is running {strategyName}'.format(name=self.name, strategyName=self.strategyName))
        self.runStrategy()

        return self.objectData


    def getTransitionName(self):
        return self.name

    def getTransitionStrategyName(self):
        return self.strategyName

    def getTransitionObject(self):
        return self.object

    def getTransitionDuration(self):
        return self.duration

    def setTransitionObjectData(self, objectData):
        self.objectData = objectData
        
    def runStrategy(self):
        self.initial()
        decisionList = []
        for currentData in self.objectData.itertuples(name='FeedData'):
            decision = self.strategy.loop(currentData, decisionList)
            self.performDecision(decision)
            decisionList.append(decision)

            self.loopIndex += 1

        self.end()

    def initial(self):
        self.strategy.tearUp()
        self.cashHistory.append(100000)
        self.positionHistory.append(0)

    def performDecision(self, decision):
        # use next open price as deal price
        price = self.getDealPrice()
        # no available price
        if price == 0:
            decision.volumn = 0
        currentCash = self.cashHistory[self.loopIndex]
        currentPosition = self.positionHistory[self.loopIndex]
        # market value depends on current cash and current object value
        # current cash and current position was calcualted in previous loop
        # for example, in day n, if decision was made for bid/ask, 
        # the cash and position wouldn't change till day n+1, because the decision was made by
        # today's close price, that's means transaction can't happend till next day.
        marketValue = currentCash + currentPosition * self.objectData.loc[self.loopIndex, 'close']

        if decision.action == BID:
            requiredCash = price * decision.volumn
            if requiredCash < currentCash:
                currentCash -= requiredCash
                currentPosition += decision.volumn
        elif decision.action == ASK:
            if currentPosition - decision.volumn >=0:
                gainCash = price * decision.volumn
                currentCash += gainCash

        if price != 0:
            self.cashHistory.append(currentCash)
            self.positionHistory.append(currentPosition)

        self.marketValue.append(marketValue)

    def getDealPrice(self):
        priceIndex = self.loopIndex + 1
        if priceIndex >= self.objectData.shape[0]:
            return 0
        else:
            return self.objectData.loc[priceIndex, 'open']

    def end(self):
        self.strategy.tearDown()
        self.calculateRoi()
        self.calculateSharp()
        self.objectData = self.objectData.assign(marketValue = self.marketValue)

    def calculateRoi(self):
        pass

    def calculateSharp(self):
        pass

