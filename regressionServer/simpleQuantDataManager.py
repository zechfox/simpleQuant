# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 20:38:19 2015

@author: zech
"""
import asyncio
import aiohttp
import datetime
import functools
import json
import logging
import re
import pandas as pd
import tushare as ts
import urllib

from common.simpleQuantLogger import SimpleQuantLogger

# 0 topic means system/framework log
logger = SimpleQuantLogger(0, '127.0.0.1:4321')



def removeDuplicated(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def _code_to_symbol(code):
    return 'sh%s'%code if code[:1] in ['5', '6'] else 'sz%s'%code

class SimpleQuantDataManager:

    def __init__(self):
        #self.stock_symbol = ''
        #self.end_date   = datetime.datetime.today()
        #deltaDays = datetime.timedelta(days=-100)
        #self.start_date = self.end_date + deltaDays 
        #self.updateStockData(self.start_date, self.end_date)
        #it's not a hard real time,
        #it's ok use list as data container,
        #all the process would be finished in timer event
        #and the design also availabe for hangqing API later,
        #due to hangqing API is still not hard real time,
        #the period will be 3sec at least
        #self.realtime_data = [0]
        self.dbAddr = 'http://q.stock.sohu.com/hisHq?code=cn_'

    def getStockData(self):
        return self.stock_data

    async def fetchPage(self, url):
        async with aiohttp.get(url) as response:
            try:
                assert response.status == 200
                logger.info("OK!", response.url)
                return await response.text()
            except AssertionError:
                logger.error('Error!', response.url, response.status) 

    """
    Parameters:
               object: object code, currently, only stock code supported
               duration: time duration, calculate from today
               filter: data filter, could close, open, high, low, volume
    """    
    async def getObjectData(self, object, duration, filter=['all']):
        endData = datetime.datetime.today()
        deltaDayas = datetime.timedelta(days=-duration)
        startData = endData + deltaDayas
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, functools.partial(ts.get_k_data, object, startData.strftime('%Y-%m-%d'), endData.strftime('%Y-%m-%d')))
        fetchedObjectData = await future
        if filter[0] == 'all':
            filterData = fetchedObjectData
        else:
            filterData = fetchedObjectData[filter]
        
        return 0, filterData.to_json()


    def filterData(self, data, filter):
        DAY_PRICE_COLUMNS = ['date', 'open', 'close', 'price_change', 'p_change', \
                             'low', 'high', 'volume', 'amount', 'turnover']
        df = pd.DataFrame(data, columns=DAY_PRICE_COLUMNS)
        if filter[0] == 'all':
            filterData = df
        else:
            filterData = df[filter]

        return filterData.to_json()

    def getStockDate(self):
        return [entry[0] for entry in self.stock_data]

    def getCurrentDataSize(self):
        return len(self.stock_data)

    def setStockContext(self, startDate, endDate):
        self.start_date = startDate
        self.end_date   = endDate
        self.updateStockData(startDate, endDate)

    def getAppendStockData(self):
        hqEntries = self.getAnother80StockData()
        appendStockData = self.stock_data + hqEntries
        return appendStockData

    def getAnother80StockData(self):
        deltaDays = datetime.timedelta(days=-1)
        startDate = self.start_date + deltaDays
        url = ('http://q.stock.sohu.com/hisHq?code=cn_' +
               self.stock_symbol + '&start=' + startDate.strftime('%Y%m%d'))
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
               self.stock_symbol + '&start=' + self.start_date.strftime('%Y%m%d') + '&end=' + self.end_date.strftime('%Y%m%d'))
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
        logger.info("setBasicData....Done!")

    def initialHistoryWindow(self, windowsSize):
        self.history_windows_size = windowsSize

    def getHistoryStockData(self):
        return self.open[self.history_data_start_index:(self.history_data_start_index + self.history_windows_size)]

    def setHistoryDataStartIndex(self, startIndex):
        self.history_data_start_index = startIndex

    def prepareHistoryData(self):
        self.setBasicData(self.getAppendStockData())
        logger.info("prepare history data....Done!")

    def getLowPrice(self):
        return self.low[self.history_windows_size + self.history_data_start_index]

    def getHighPrice(self):
        return self.high[self.history_windows_size + self.history_data_start_index]

    #called by online timer handler of transition
    def retreiveRealTimeQuotes(self):
        logger.info("retreive real time quotes")
        stockSymbol = _code_to_symbol(self.stock_symbol)
        url = ('http://hq.sinajs.cn/list=' + stockSymbol)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            roughData = response.read().decode('GBK')
        reg = re.compile(r'\="(.*?)\";')
        data = reg.findall(roughData)
        regSym = re.compile(r'(?:sh|sz)(.*?)\=')
        syms = regSym.findall(roughData)
        data_list = []
        syms_list = []
        for index, row in enumerate(data):
            if len(row)>1:
                data_list.append([astr for astr in row.split(',')])
                syms_list.append(syms[index])

        #only support 1 symbol now
        if self.realtime_data[-1] != data_list:
            self.realtime_data.append(data_list)

    def getLatestRealTimeQuotes(self, numbers):
        #return null if no enough data
        logger.info("get latest %d real time quotes", numbers)
        dataLength = len(self.realtime_data)
        if dataLength > numbers:
            return self.realtime_data[(dataLength - numbers):-1]
        else:
            return []
