# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 20:57:03 2015

@author: zech
"""
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from simpleQuantDataManager import SimpleQuantUIDataManager
#from simpleQuantStrategy import SimpleQuantStrategyBase
from simpleQuantStrategyManager import SimpleQuantStrategyManager
import datetime
from matplotlib.dates import DateFormatter
    
class SimpleQuantUIStaticMplCanvas(FigureCanvas):
    def __init__(self, hq_data = 0):
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)
        daysFmt  = DateFormatter('%Y-%m-%d')
        self.axes.xaxis.set_major_formatter(daysFmt)
        self.axes.autoscale_view()
        # format the coords message box  
        def price(x): return '$%1.2f'%x
        self.axes.fmt_xdata = DateFormatter('%Y-%m-%d')
        self.axes.fmt_ydata = price
        self.axes.grid(True)
        self.fig.autofmt_xdate()
        self.updateFigure(hq_data)
        #
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def updateFigure(self, hq_data):
        dates = [datetime.datetime.strptime(entry[0],"%Y-%m-%d") for entry in hq_data]
        opens = [entry[1] for entry in hq_data]
        self.axes.plot(dates, opens, 'r')
        self.fig.autofmt_xdate()
        
        
class SimpleQuantUIStrategyMplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.axes = self.fig.add_subplot(111)
        #the axes cleared every time plot() is called
        self.axes.hold(False)
        daysFmt  = DateFormatter('%Y-%m-%d')
        self.axes.xaxis.set_major_formatter(daysFmt)
        self.axes.autoscale_view()
        # format the coords message box  
        def price(x): return '$%1.2f'%x
        self.axes.fmt_xdata = DateFormatter('%Y-%m-%d')
        self.axes.fmt_ydata = price
        self.axes.grid(True)
        self.fig.autofmt_xdate()
        #
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def updateFigure(self, profits_data):
        dates = [datetime.datetime.strptime(entry[0],"%Y-%m-%d") for entry in profits_data]
        profits = [entry[1] for entry in profits_data]
        self.axes.plot(dates, profits, 'r')
        self.fig.autofmt_xdate()
        
        
class SimpleQuantUITransitionDialog(QtGui.QDialog):
    def __init__(self, stockSymbol):
        QtGui.QDialog.__init__(self)
        #today is endDate, startDate is earlier than endDate
        endDate = QtCore.QDate.currentDate()
        startDate = endDate.addDays(-60)
        self.strategy_manager = SimpleQuantStrategyManager()
        self.data_manager = SimpleQuantUIDataManager(stockSymbol, startDate, endDate)
        #self.stock_strategy = SimpleQuantStrategyMACD(self.data_manager)
        self.setGeometry(100, 100, 850, 650)
        self.main_widget = QtGui.QWidget(self)
        self.start_date = QtGui.QDateEdit(self)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(startDate)
        startDateLabel = QtGui.QLabel('StartDate: ', self)
        self.end_date = QtGui.QDateEdit(self)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(endDate)
        endDateLabel = QtGui.QLabel('EndDate: ', self)
        self.update_button = QtGui.QPushButton("Update")
        self.update_button.clicked.connect(self.updateButtonClicked)
        self.transition_layout = QtGui.QVBoxLayout(self.main_widget)
        self.stock_layout = QtGui.QHBoxLayout()
        self.stock_widget_layout = QtGui.QVBoxLayout()
        self.stock_widget_layout.addWidget(startDateLabel)
        self.stock_widget_layout.addWidget(self.start_date)
        self.stock_widget_layout.addWidget(endDateLabel)
        self.stock_widget_layout.addWidget(self.end_date)
        hqData = self.data_manager.getStockData()
        self.stock_canvas = SimpleQuantUIStaticMplCanvas(hqData)
        self.stock_layout.addStretch(1)
        self.stock_layout.addWidget(self.stock_canvas)
        self.stock_layout.addLayout(self.stock_widget_layout)
        self.stock_layout.addWidget(self.update_button)
        
        self.strategy_layout = QtGui.QHBoxLayout()
        self.strategy_button = QtGui.QPushButton("Run")
        self.strategy_button.clicked.connect(self.strategyButtonClicked)
        self.strategy_combobox = QtGui.QComboBox()
        self.strategy_combobox.activated[str].connect(self.strategyChanged)
        [self.strategy_combobox.addItem(strategyName) for strategyName in self.strategy_manager.getStrategyNameList()]
        self.strategy_canvas = SimpleQuantUIStrategyMplCanvas()
        self.strategy_layout.addStretch(1)
        self.strategy_layout.addWidget(self.strategy_canvas)
        self.strategy_layout.addWidget(self.strategy_button)
        self.strategy_layout.addWidget(self.strategy_combobox)
        
        self.transition_layout.addLayout(self.stock_layout)
        self.transition_layout.addLayout(self.strategy_layout)
        
    def updateButtonClicked(self):
        endDate = self.end_date.date()
        startDate = self.start_date.date()
        self.data_manager.setStockContext(startDate, endDate)
        stockData = self.data_manager.getStockData()
        self.stock_canvas.updateFigure(stockData)
        self.stock_canvas.draw()
        
    def strategyButtonClicked(self):
        self.stock_strategy = self.strategy_manager.getStrategyInstance()(self.data_manager)
        profitsData = self.stock_strategy.backTest()
        self.strategy_canvas.updateFigure(profitsData)
        self.strategy_canvas.draw()
        print("Done!")
        
    def strategyChanged(self, strategyName):
        self.strategy_manager.setStrategyName(strategyName)
        

        
class SimpleQuantUIMainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.setGeometry(100, 100, 750, 450)
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        self.Hlayout = QtGui.QHBoxLayout(self.main_widget)
        
        self.quaryButton = QtGui.QPushButton("Quary Data", self)
        self.quaryText = QtGui.QLineEdit(self)
        self.Hlayout.addWidget(self.quaryText)
        self.Hlayout.addWidget(self.quaryButton)
        self.quaryButton.clicked.connect(self.quaryButtonClicked)
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def quaryButtonClicked(self):
        stockSymbol = self.quaryText.text()
        self.transitionUI = SimpleQuantUITransitionDialog(stockSymbol)
        self.transitionUI.show()
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
)