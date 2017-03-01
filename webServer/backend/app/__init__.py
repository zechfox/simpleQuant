# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:39:40 2015

@author: zech
"""
import os, sys, inspect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

static_folder_root = os.path.join(os.path.abspath(os.path.join(__file__, '../../../')), "frontend")
work_dir = os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])
project_root_dir = os.path.realpath(work_dir + '../../../../')
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

app = Flask(__name__, static_folder=static_folder_root, static_url_path='')
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+work_dir+'/transitions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from app import views
db.create_all()
