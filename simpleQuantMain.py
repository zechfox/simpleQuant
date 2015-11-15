# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 21:28:35 2015

@author: zech
"""
import sys
from simpleQuantUI import *


#----------------------------------------------------------------------
def main():
    
    qApp = QtGui.QApplication(sys.argv)
    aw = SimpleQuantUIMainWindow()
    aw.setWindowTitle("simpleQuant")
    aw.show()
    sys.exit(qApp.exec_())
    
if __name__ == '__main__':
    main()