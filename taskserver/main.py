
import os

from anyserver import TemplateRouter

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Define a router that we can load some routes into
router = TemplateRouter(prefix='/taskserver', base=f'{THIS_DIR}/templates')
