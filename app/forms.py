# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 10:53:02 2016

@author: zech
"""
import datetime

from flask_wtf import Form
from wtforms import StringField, SelectField, TextField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField

class MainSearchForm(Form):
    stockSymbol = StringField('stockSymbol', validators=[DataRequired()], description={'placeholder': 'search for stock symbols'})

class TransitionPanelForm(Form):
    endDate = datetime.datetime.today()
    deltaDays = datetime.timedelta(days=-60)
    startDate = endDate + deltaDays
    startDateField = DateField('Start Date', default=startDate, format='%Y-%m-%d')
    endDateField = DateField('End Date', default=endDate, format='%Y-%m-%d')
    strategyListField = SelectField(u'Strategy List')

class StrategyEditorForm(Form):
    strategyNameField    = TextField(u'StrategyName', validators=[DataRequired()])
    strategyEditorField = TextAreaField(u'StrategyEditor', validators=[DataRequired()])
    
class StrategyHrefName():
    def __init__(self, name):
      self.href = '/manageStrategy/' + name
      self.name = name