import os
from anyserver import TemplateRouter
from taskserver.models.TaskfileServer import TaskfileServer

# Define a router that we can load some routes into
this_dir = os.path.dirname(os.path.realpath(__file__))
router = TemplateRouter(prefix='/task', base=f'{this_dir}/templates')

task_server = TaskfileServer()
