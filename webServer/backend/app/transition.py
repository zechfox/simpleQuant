import json 

from app import db

class Transition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    strategyName = db.Column(db.String(120), unique=False)
    object = db.Column(db.String(120), unique=False)
    duration = db.Column(db.Integer, unique=False)
    customizeParameter = db.Column(db.String(1024), unique=False)

    def __init__(self, name, strategyName, object):
        self.name = name
        self.strategyName = strategyName 
        self.object = object
        self.duration = 100 
        self.customizeParameter = ''

    def toJSON(self):
        return json.dumps(self.toDict())

    def toDict(self):
        print(self.customizeParameter)
        return {"id": self.id,
                "name": self.name,
                "strategyName": self.strategyName,
                "object": self.object,
                "duration": self.duration,
                "customizeParameter": self.customizeParameter
               }

    def updateFromDict(self, dict):

        self.name = dict['name']
        # strategy changed, the customize parameter maybe changed too
        # update customize parameter later by quaring isParameterDirty()
        if(self.strategyName == dict['strategyName']):
            self.customizeParameter = dict['customizeParameter']
        else:
            self.customizeParameter = ''

        self.strategyName = dict['strategyName']
        self.object = dict['object']
        self.duration = dict['duration']

    def isParametersEmpty(self):
        print(self.customizeParameter)
        return self.customizeParameter == ''

    def setCustomizeParameter(self, parameters):
        self.customizeParameter = parameters;


    def __repr__(self):
        return '<User %r>' % self.name

