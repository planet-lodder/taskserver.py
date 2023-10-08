from anyserver import TemplateRouter
from taskserver.task.models.TaskfileServer import TaskfileServer

# Define a router that we can load some routes into
router = TemplateRouter(prefix='/task')
task_server = TaskfileServer()


@router.get('')
@router.renders('task/list')
def taskMain(req, resp):
    # TODO: Load from resolver
    # taskfile = taskfile_for(req)
    taskfile = {"_path": task_server.location}
    res = {
        "title": "Show All",
        "toolbar": "task/toolbar/list.html",
        "taskfile": taskfile,
        "list": task_server.list()
    }
    return res
