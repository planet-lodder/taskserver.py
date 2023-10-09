import os

from anyserver import TemplateRouter
from taskserver.models.TaskfileServer import TaskfileServer

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Define a router that we can load some routes into
router = TemplateRouter(prefix='/task', base=f'{THIS_DIR}/templates')

task_server = TaskfileServer()
