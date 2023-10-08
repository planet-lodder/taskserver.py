from anyserver import TemplateRouter
from backend.task.models.TaskfileServer import TaskfileServer

# Define a router that we can load some routes into
router = TemplateRouter(prefix='/task')
taskserver = TaskfileServer()


@router.get('')
@router.renders('task/list')
def taskMain(req, resp):
    # TODO: Load from resolver
    # taskfile = taskfile_for(req)
    taskfile = {"_path": taskserver.location}
    res = {
        "title": "Show All",
        "toolbar": "task/toolbar/list.html",
        "taskfile": taskfile,
        "list": taskserver.list()
    }
    return res
