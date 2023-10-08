from taskserver.task import router, task_server
from taskserver.task.models.TaskNode import TaskNode
from taskserver.task.models.TaskfileConfig import taskfile_for
from taskserver.task.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())


@router.get('/sidenav')
@router.renders('task/sidenav/index')
def taskMain(req, resp):
    taskfile = taskfile_for(req)
    res = {
        "title": "Show All",
        "toolbar": "task/toolbar/list.html",
        "taskfile": taskfile,
        "menu": root,
    }
    return res


@router.post('/sidenav/toggle')
@router.renders('task/sidenav/menu-item')
def taskMain(req, resp):
    htmx = HtmxRequest(req)
    key = htmx.triggerName
    node = root.find(key)
    if node:
        node.open = not node.open
    return {
        "item": node,
    }
