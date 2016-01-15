# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:34:26 2015

@author: zech
"""
import sys
import importlib
import pkgutil
import inspect
import strategy
from simpleQuantStrategy import SimpleQuantStrategyBase
import logging

MyLogger = logging.getLogger(__name__)
class SimpleQuantStrategyManager:
    def __init__(self):
        self.strategy_name_list = [modname for importer, modname, ispkg in pkgutil.iter_modules(strategy.__path__)]
        self.setStrategyName(self.strategy_name_list[0])

    def getStrategyInstance(self):
        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module("strategy." + self.strategy_name)
        for name, obj in inspect.getmembers(m, inspect.isclass):
            if issubclass(obj, SimpleQuantStrategyBase) and (obj != SimpleQuantStrategyBase):
                return obj

    def setStrategyName(self, strategyName):
        MyLogger.info("set strategy name")
        self.strategy_name = strategyName

    def getStrategyNameList(self):
        return self.strategy_name_list