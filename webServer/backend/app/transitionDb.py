import json 
import sqlalchemy as sa

meta = sa.MetaData()

# aiopg.sa utilized sqlachemy by dirty hacks without support declarative
# hope later version can support it.
class TransitionDb():
    transition = sa.Table(
        'transition', meta,
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.String(80), nullable=False, unique=True),
        sa.Column('strategy_name', sa.String(120), unique=False),
        sa.Column('object', sa.String(120), unique=False),
        sa.Column('duration', sa.Integer, unique=False),
        sa.Column('customize_parameter', sa.String(1024), unique=False))

    @classmethod
    async def queryDbByName(cls, conn, name):
        result = await conn.execute(
            cls.transition.select()
            .where(cls.transition.c.name == name))
        transition = await result.first()
        if transition:
            return cls(transition.name,
                       transition.strategy_name, 
                       transition.object,
                       transition.customize_parameter,
                       transition.id) 
        else:
            return None

    @classmethod
    async def queryDbById(cls, conn, id):
        result = await conn.execute(
            cls.transition.select()
            .where(cls.transition.c.id == id))
        transition = await result.first() 
        return cls(transition.name,
                   transition.strategy_name, 
                   transition.object,
                   transition.customize_parameter,
                   transition.id) 
                  

    @classmethod
    async def getAll(cls, conn):
        result = await conn.execute(
            cls.transition.select())
        records = await result.fetchall()
        transitions = []
        for transition in records:
            transitions.append(cls(transition.name, 
                                   transition.strategy_name, 
                                   transition.object,
                                   transition.customize_parameter,
                                   transition.id)) 
        return transitions

    def __init__(self, name, strategyName, object, parameters, id=''):
        self.name = name
        self.strategyName = strategyName 
        self.object = object
        self.duration = 100 
        self.customizeParameter = parameters
        self.id = id


    def toJSON(self):
        return json.dumps(self.toDict())

    def toDict(self):
        return {"id": self.id,
                "name": self.name,
                "strategyName": self.strategyName,
                "object": self.object,
                "duration": self.duration,
                "customizeParameter": self.customizeParameter
               }

    async def insertDb(self, conn):
        id = await conn.scalar(
                     TransitionDb.transition.insert()
                     .values(name=self.name,
                             strategy_name=self.strategyName,
                             object=self.object,
                             duration=self.duration,
                             customize_parameter=self.customizeParameter))
        if not id:
            print("Insert Transition id:{id} failed.".format(id=id))
        else:
            self.id = id
                                          

    async def updateDb(self, conn):
        result = await conn.execute(
                     TransitionDb.transition.update()
                     .returning(*TransitionDb.transition.c)
                     .where(TransitionDb.transition.c.id == self.id)
                     .values(id=self.id, 
                             name=self.name,
                             strategy_name=self.strategyName,
                             object=self.object,
                             duration=self.duration,
                             customize_parameter=self.customizeParameter))
        record = await result.fetchone()
        if not record:
            print("Update Transition id:{id} failed.".format(id=self.id))


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
        return self.customizeParameter == ''

    def setCustomizeParameter(self, parameters):
        self.customizeParameter = parameters;


    def __repr__(self):
        return '<User %r>' % self.name

