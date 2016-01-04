# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:39:40 2015

@author: zech
"""

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from app import views