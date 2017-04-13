# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:41:01 2015

@author: zech
"""
#!flask/bin/python
import os
import sys
import inspect



#----------------------------------------------------------------------
    

if __name__ == '__main__':
    project_root_dir = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])+'../../')
    print(project_root_dir)
    if project_root_dir not in sys.path:
        sys.path.insert(0, project_root_dir)

    from backend.app import aioApp
    aioApp.run(sys.argv[1:])
