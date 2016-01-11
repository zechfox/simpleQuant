# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 10:53:02 2016

@author: zech
"""

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField

class MainSearchForm(Form):
    stockSymbol = StringField('stockSymbol', validators=[DataRequired()], description={'placeholder': 'search for stock symbols'})
    
class TransitionPanelForm(Form):
    startDateField = DateField('DatePicker', format='%Y-%m-%d')
    endDateField = DateField('DatePicker', format='%Y-%m-%d')