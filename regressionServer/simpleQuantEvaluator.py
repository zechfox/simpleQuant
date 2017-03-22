# -*- coding: utf-8 -*-
"""
Created on TUE MAR 21 2017

@author: zech
"""

import sys


class SimpleQuantEvaluator:
    def __init__(self):
        
      self.report = {'ROI':0, 'MaxDrawback':0, 'MaxGain':0}

    """ 
       generate a evaluate report for transtion
       Parameter: None
       Return: Dictionary which contains: ROI, Max Drawback, Max Gain, and so on
    """
    def getReport(self):
      return self.report

    def performEvaluate(self, transition):
      valueHistory = transition.marketValue
      cashHistory = transition.cashHistory
      self.report['MaxGain'] = max(valueHistory)
      self.report['MaxDrawback'] = min(valueHistory)
      self.report['ROI'] = valueHistory[-1]/cashHistory[0] - 1
      

