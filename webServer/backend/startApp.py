# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:41:01 2015

@author: zech
"""
#!flask/bin/python
import os
import sys
import inspect
import threading
import logging
import logging.handlers


from app import app

#----------------------------------------------------------------------
def startApp():
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    fileHandler = logging.FileHandler(os.path.splitext(__file__)[0] + '.log')
    fileHandler.setFormatter(formatter)
    rootLogger.addHandler(fileHandler)

    try:
        #set debug true will start main() twice, one for start main(), the other for monitor project modification
        sys.exit(app.run(debug = False, host='0.0.0.0'))
    except(KeyboardInterrupt, SystemExit):
        recv.shutdown()
        sys.exit()


if __name__ == '__main__':
    project_root_dir = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])+'../../../')
    if project_root_dir not in sys.path:
        sys.path.insert(0, project_root_dir)
    startApp()
