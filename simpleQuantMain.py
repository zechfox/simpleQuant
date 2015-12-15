# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 21:28:35 2015

@author: zech
"""
import os
import sys
import logging
import logging.handlers
import threading
from simpleQuantUI import *
import simpleQuantLogger


#----------------------------------------------------------------------
def main():
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    fileHandler = logging.FileHandler(os.path.splitext(__file__)[0] + '.log')
    fileHandler.setFormatter(formatter)
    rootLogger.addHandler(fileHandler)

    recv = simpleQuantLogger.LoggingReceiver()
    thr_recv = threading.Thread(target=recv.serve_forever)
    thr_recv.daemon = True
    print('%s started at %s' % (recv.__class__.__name__, recv.server_address))
    thr_recv.start()    
    
    qApp = QtGui.QApplication(sys.argv)
    aw = SimpleQuantUIMainWindow()
    aw.setWindowTitle("simpleQuant")
    aw.show()
    try:
      sys.exit(qApp.exec_())
    except(KeyboardInterrupt, SystemExit):
      recv.shutdown()
      sys.exit()
    
if __name__ == '__main__':
    main()