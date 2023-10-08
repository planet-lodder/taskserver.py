from taskserver import router, task_server
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())


@router.get('/sidenav')
@router.renders('sidenav/index')
def taskMain(req, resp):
    taskfile = taskfile_for(req)
    res = {
        "title": "Show All",
        "toolbar": "partials/toolbar/list.html",
        "taskfile": taskfile,
        "menu": root,
    }
    return res


@router.post('/sidenav/toggle')
@router.renders('sidenav/menu-item')
def taskMain(req, resp):
    htmx = HtmxRequest(req)
    key = htmx.triggerName
    node = root.find(key)
    if node:
        node.open = not node.open
    return {
        "item": node,
    }
