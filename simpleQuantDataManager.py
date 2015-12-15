# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 20:38:19 2015

@author: zech
"""
import urllib
import json
import logging

MyLogger = logging.getLogger(__name__)   

def removeDuplicated(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]
    
class SimpleQuantUIDataManager:
        
    def __init__(self, stockSymbol, startDate, endDate):
        self.stock_symbol = stockSymbol
        self.start_date = startDate
        self.end_date   = endDate
        self.updateStockData(startDate, endDate)
        
    def getStockData(self):
        return self.stock_data
        
    def getStockDate(self):
        return [entry[0] for entry in self.stock_data]
        
    def getCurrentDataSize(self):
        return len(self.stock_data)
        
    def setStockContext(self, startDate, endDate):
        self.start_date = startDate
        self.end_date   = endDate
        self.updateStockData(startDate, endDate)
        
    def getAppendStockData(self, startDate):
        
        hqEntries = self.getAnother80StockData(startDate)
        appendStockData = self.stock_data + hqEntries
        return appendStockData

    def getAnother80StockData(self, startDate):
        url = ('http://q.stock.sohu.com/hisHq?code=cn_' +
               self.stock_symbol + '&start=' + self.start_date.addDays(-1).toString('yyyyMMdd'))
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:        
            json_data = response.read().decode()
        #json_date is a single object JSON, 
        #json.load() convert it to a list that contain a dict
        #so, use get dict out by [0]
        #hqEntries is a list
        hqEntries = json.loads(json_data)[0]['hq']
        return hqEntries
    
    def updateStockData(self, startDate, endDate):
        url = ('http://q.stock.sohu.com/hisHq?code=cn_' +
               self.stock_symbol + '&start=' + self.start_date.toString('yyyyMMdd') + '&end=' + self.end_date.toString('yyyyMMdd'))
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:        
            json_data = response.read().decode()
        #json_date is a single object JSON, 
        #json.load() convert it to a list that contain a dict
        #so, use get dict out by [0]
        #hqEntries is a list
        self.stock_data = json.loads(json_data)[0]['hq']
        
    def setBasicData(self, roughData):
        #unzip rough_data, then zip them as list of tuple
        (self.date, self.open, self.close, self.change, self.chg_percent, self.low,
         self.high, self.volume, self.turnover, self.tunrover_rate) = zip(*(roughData[::-1]))
        MyLogger.info("setBasicData....Done!")
         
    def initialHistoryWindow(self, windowsSize):
        self.history_windows_size = windowsSize
        
    def getHistoryStockData(self):
        return self.open[self.history_data_start_index:(self.history_data_start_index + self.history_windows_size)]
    
    def setHistoryDataStartIndex(self, startIndex):
        self.history_data_start_index = startIndex
        
    def prepareHistoryData(self):
        self.setBasicData(self.getAppendStockData(self.end_date))
        MyLogger.info("prepare history data....Done!")
        
    def getLowPrice(self):
        return self.low[self.history_windows_size + self.history_data_start_index]
        
    def getHighPrice(self):
        return self.high[self.history_windows_size + self.history_data_start_index]
        