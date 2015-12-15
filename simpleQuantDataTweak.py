# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 21:34:04 2015

@author: zech
"""
import numpy as np
import logging

MyLogger = logging.getLogger(__name__)   

class SimpleQuantDataTweak:
    def __init__(self):
        pass
    
    def movingAverage(self, x, n, type='simple'):
        """
        compute an n period moving average.
        type is 'simple' | 'exponential'
        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))
            
        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a
        
    def movingAverageConvergence(self, x, nslow=26, nfast=12, nema=9):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = self.movingAverage(x, nslow, type='exponential')
        emafast = self.movingAverage(x, nfast, type='exponential')
        dif = emafast - emaslow
        macd = self.movingAverage(dif, nema, type='exponential')
        return dif, dif - macd, macd
        
        
    