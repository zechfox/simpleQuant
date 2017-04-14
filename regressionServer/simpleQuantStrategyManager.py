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
from common.simpleQuantLogger import SimpleQuantLogger

logger = SimpleQuantLogger(__name__, '127.0.0.1:4321')

class SimpleQuantStrategyManager:
    def __init__(self):
        self.strategy_name_list = [modname for importer, modname, ispkg in pkgutil.iter_modules(strategy.__path__)]

    def getStrategyInstance(self, strategyName):
        # load the module, will raise ImportError if module cannot be loaded
        if strategyName in self.strategy_name_list:
            m = importlib.import_module("strategy." + strategyName)
            for name, obj in inspect.getmembers(m, inspect.isclass):
                if issubclass(obj, SimpleQuantStrategyBase) and (obj != SimpleQuantStrategyBase):
                    return obj
        logger.info('No strategy was found with name:{strategyName}'.format(strategyName=strategyName))

    def getStrategyNameList(self):
        return self.strategy_name_list

    def getStretegyCustomizeParameters(self, strategyName):
        if strategyName in self.strategy_name_list:
            m = importlib.import_module("strategy." + strategyName)
            if(hasattr(m, 'customizeParameterList')):
              parametersList = m.customizeParameterList
            else:
              parametersList = []
            return 0, parametersList 
        else:
            return -1, []

    def getStrategySourceCode(self, strategyName):
        logger.info('SimpleQuantStrategyManager:getStrategySourceCode() strategyName:{strategyName}'.format(strategyName=strategyName))
        if strategyName in self.strategy_name_list:
            fileName = "strategy/" + strategyName + '.py'
            with open(fileName, 'r') as f:
                read_data = f.read()
            f.close()
            return 0, read_data
        else: 
            return -1, []

