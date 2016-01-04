# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 10:53:02 2016

@author: zech
"""

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class MainSearchForm(Form):
    stockSymbol = StringField('stockSymbol', validators=[DataRequired()], description={'placeholder': 'search for stock symbols'})