import argparse
import aiopg.sa
import asyncio
import sys
import trafaret as T
import zmq

from aiohttp import web
from trafaret_config import commandline
from routes import setup_routes

primitive_ip_regexp = r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'

TRAFARET = T.Dict({
    T.Key('postgres'):
        T.Dict({
            'database': T.String(),
            'user': T.String(),
            'password': T.String(),
            'host': T.String(),
            'port': T.Int(),
            'minsize': T.Int(),
            'maxsize': T.Int(),
        }),
    T.Key('host'): T.String(regex=primitive_ip_regexp),
    T.Key('port'): T.Int(),
})

async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=app.loop)
    app['db'] = engine

async def init_regression(app):
    serverAddr = '127.0.0.1:1234'
    msg = ['connectionReq', {'name':'zechfox'}]
    context = zmq.Context()
    sock = context.socket(zmq.REQ)
    sock.connect('tcp://%s:%s' % ('127.0.0.1', 1234))
    sock.send_json(msg)
    connectionCfm = sock.recv_json()
    app['regrSock'] = sock



async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()

def init(loop, argv):
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(ap,
                                          default_config='../config/config.yaml')
    #
    # define your command-line arguments here
    #
    options = ap.parse_args(argv)

    config = commandline.config_from_options(options, TRAFARET)

    # setup application and extensions
    app = web.Application(loop=loop)

    # load config from yaml file in current dir
    app['config'] = config

    # create connection to the database
    app.on_startup.append(init_pg)
    # shutdown db connection on exit
    app.on_cleanup.append(close_pg)

    # create connection to regression server
    app.on_startup.append(init_regression)
    # setup views and routes
    setup_routes(app)

    return app 

def main(argv):
    # init logging

    loop = asyncio.get_event_loop()

    app = init(loop, argv)
    web.run_app(app,
                host=app['config']['host'],
                port=app['config']['port'])
if __name__ == '__main__':
    main(sys.argv[1:])
