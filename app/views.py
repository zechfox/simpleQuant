# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:40:08 2015

@author: zech
"""
import os
import datetime
from multiprocessing import Queue
from flask import render_template, flash, redirect, session
import json

from app import app
from .forms import MainSearchForm, TransitionPanelForm, StrategyEditorForm
from .forms import StrategyHrefName
from simpleQuantTransition import SimpleQuantTransition
from simpleQuantStrategyManager import SimpleQuantStrategyManager
from simpleQuantDataManager import SimpleQuantUIDataManager

feedback_queue = Queue()

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
    stockSymbol = session.get('stockSymbol')
    strategyManager = SimpleQuantStrategyManager()

    transitionPanelForm.strategyListField.choices = [(name, name) for name in strategyManager.getStrategyNameList()]


    if transitionPanelForm.validate_on_submit():
        #TODO: run strategy in new process
        #1. start transition in new process
        #2. display page as well. wait until transition finish. It's no need render template instantly after strat transtion,
        #   because javascript can display page as well when click 'start strategy', while in backend, parent process wait for
        #   transition process finish, then render the template again, the well will disapear.
        #3. render the template
        strategyName = transitionPanelForm.strategyListField.data
        startDate = transitionPanelForm.startDateField.data
        endDate = transitionPanelForm.endDateField.data

        transition = SimpleQuantTransition(stockSymbol, strategyName, startDate, endDate, feedback_queue)
        transition.start()

        #wait transition finish
        transition.join()

        return render_template("transition.html",
                               title = 'Trasition',
                               transitionPanelForm = transitionPanelForm)
    else:
        endDate = datetime.datetime.today()
        deltaDays = datetime.timedelta(days=-60)
        startDate = endDate + deltaDays
        dataManager = SimpleQuantUIDataManager(stockSymbol, startDate, endDate)
        hqData = dataManager.getStockData()
        with open('app/static/json/hqData.json', 'w') as f:
            f.write(json.dumps(hqData))


    return render_template("transition.html",
                           title = 'Trasition',
                           transitionPanelForm = transitionPanelForm)

@app.route('/manageStrategy', methods=['GET','POST'])
@app.route('/manageStrategy/<string:page>', methods=['GET','POST'])
def manageStrategy(page = ''):
    #1. check page is valid or not, if page not empty
    #2. if page = '' or not valid, list all strategy name
    #3. if page = valid strategy name, render strategy editor with preload strategy code
    #4. if page = 'newStrategy', render strategy editor with preload strategy template code
    strategyEditorForm = StrategyEditorForm()
    strategyManager = SimpleQuantStrategyManager()
    strategyNameList = strategyManager.getStrategyNameList()
    strategyHrefNameList = [StrategyHrefName(name) for name in strategyNameList]

    if strategyEditorForm.validate_on_submit():
        print("submit strategy")
        newStrategyName = strategyEditorForm.strategyNameField.data
        if newStrategyName not in strategyNameList:
          newStrategyCode = strategyEditorForm.strategyEditorField.data
          strategyFilePath = os.path.join(os.path.dirname(__file__) + '/../strategy/' + newStrategyName + '.py')
          fo = open(strategyFilePath, 'w')
          fo.write(newStrategyCode)
          fo.close()
          return redirect('/manageStrategy')
        else:
          #TODO: prompt error when strategy name exist
          strategyEditorForm.strategyNameField.errors = 'Strategy Name has exist, please try another one!'
          return redirect('/manageStrategy/newStrategy')

    elif page == 'newStrategy':
        print("new Strategy")
        strategyHrefNameList.clear()
        return render_template('editor.html',
                    title = 'StrategyEditor',
                    strategyEditorForm = strategyEditorForm,
                    strategyHrefNameList = strategyHrefNameList)
    elif page in strategyNameList:
        #render strategy editor with preload strategy code
        print("submit OK")
        strategyHrefNameList.clear()
        strategyEditorForm.strategyNameField.data = page
        strategyFilePath = os.path.join(os.path.dirname(__file__) + '/../strategy/' + page + '.py')
        fo = open(strategyFilePath, 'r')
        strategyEditorForm.strategyEditorField.data = fo.read()
        fo.close()
        return render_template('editor.html',
                    title = 'StrategyEditor',
                    strategyEditorForm = strategyEditorForm,
                    strategyHrefNameList = strategyHrefNameList)
    else:
        #page = '' or not in strategy name or not valid
        #render as /manangeStrategy
        print("submit NOT OK")

    return render_template('editor.html',
                           title = 'StrategyEditor',
                           strategyEditorForm = strategyEditorForm,
                           strategyHrefNameList = strategyHrefNameList)