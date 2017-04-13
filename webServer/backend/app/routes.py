import os, sys, inspect
from .aioAppViews import index, transitions, getStrategies, getStrategyData, getTransitionData, updateTransition
static_folder_root = os.path.join(os.path.abspath(os.path.join(__file__, '../../../')), "frontend")

def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/transitions', transitions)
    app.router.add_post('/transitions', transitions)
    app.router.add_get('/strategies', getStrategies)
    resource = app.router.add_resource('/strategy/detail/{name}/{data}')
    resource.add_route('GET', getStrategyData)
    resource = app.router.add_resource('/transition/detail/{transitionId:\d+}/{data}')
    resource.add_route('GET', getTransitionData)
    resource = app.router.add_resource('/transition/detail/{transitionId:\d+}')
    resource.add_route('POST', updateTransition)

    #put static at last
    app.router.add_static('/', static_folder_root)
