from functools import reduce
from anyserver import TemplateRouter
import yaml

from taskserver.task import router, task_server
from taskserver.task.models.TaskNode import TaskNode
from taskserver.task.models.TaskfileConfig import taskfile_for
from taskserver.task.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())


@router.get('/details')
@router.renders('task/single')
def taskView(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)

    if task and not task.value:
        # Not a leaf node, so show the search results instead
        search = task.key + ':'
        return router.render_template('task/list.html', {
            "title": search + '*',
            "search": search,
            "toolbar": "task/toolbar/list.html",
            "taskfile": taskfile,
            "list": task_server.filter(search)
        })
    
    # Show the task view
    return {
        "title": task.key if task else "unknown",
        "toolbar": "task/toolbar/task.html",
        "taskfile": taskfile,
        "task": task,
    }

@router.get('/view/history')
@router.renders('task/views/history')
def taskRunHistory(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    return {
        "title": f'{task.key} - Run History',
        "toolbar": "task/toolbar/task.html",
        "taskfile": taskfile,
        "task": task,
    }

@router.get('/view/dep-graph')
@router.renders('task/views/dep-graph')
def taskDependencyGraph(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    return {
        "title": f'{task.key} - Dependency Graph',
        "toolbar": "task/toolbar/task.html",
        "taskfile": taskfile,
        "task": task,
    }
