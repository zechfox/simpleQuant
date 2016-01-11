# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:40:08 2015

@author: zech
"""
from flask import render_template, flash, redirect, session
import json

from app import app
from .forms import MainSearchForm, TransitionPanelForm
from simpleQuantTransition import SimpleQuantTransition


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    mainSearchForm = MainSearchForm()
    if mainSearchForm.validate_on_submit():
        flash('Search for StockSymbol="' + mainSearchForm.stockSymbol.data + '"')
        session['stockSymbol'] = mainSearchForm.stockSymbol.data
        return redirect('/transition')
    return render_template("index.html",
                           title = 'Main',
                           mainSearchForm = mainSearchForm)
  
@app.route('/transition', methods=['GET','POST'])
def transition():
    transitionPanelForm = TransitionPanelForm()
    if transitionPanelForm.validate_on_submit():
        startDate = transitionPanelForm.startDateField.data
        endDate = transitionPanelForm.endDateField.data
        print(startDate.strftime('%Y-%m-%d'))
        print(endDate.strftime('%Y-%m-%d'))
        stockSymbol = session.get('stockSymbol')
        transition = SimpleQuantTransition(stockSymbol)
        transition.updateTransitionContext(startDate, endDate)
        hqData = transition.getStockData()
        profits = transition.runStrategy()
    
        with open('app/static/json/hqData.json', 'w') as f:
            f.write(json.dumps(hqData))
        with open('app/static/json/profits.json', 'w') as f:
            f.write(json.dumps(profits))
        return redirect('/transition')
    
    return render_template("transition.html",
                           title = 'Trasition',
                           transitionPanelForm = transitionPanelForm)