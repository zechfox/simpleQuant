"""
Created on 2017/02/09
@author: zechfox
@contact: zechfox@gmail.com
"""

from simpleQuantConstants import *

class SimpleQuantDecision:
    def __init__(self):
        self.action = BID
        self.volumn = 0

    def getAction(self):
        return self.action
    def getVolumn(self):
        return self.volumn
    def setAction(self, action):
        self.action = action
    def setVolumn(self, volumn):
        self.volumn = volumn
