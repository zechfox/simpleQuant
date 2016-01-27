# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:41:01 2015

@author: zech
"""
#!flask/bin/python
import os
import sys
import threading
import logging
import logging.handlers

import simpleQuantLogger

from app import app

#----------------------------------------------------------------------
def startApp():
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
    try:
        #set debug true will start main() twice, one for start main(), the other for monitor project modification
        sys.exit(app.run(debug = False))
    except(KeyboardInterrupt, SystemExit):
        recv.shutdown()
        sys.exit()


if __name__ == '__main__':
    startApp()