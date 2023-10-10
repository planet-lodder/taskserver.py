from functools import reduce
from anyserver import TemplateRouter
import yaml

from taskserver import router, task_server
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.details import TaskDetailUseCase
from taskserver.domain.use_cases.list import TaskListUseCase
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())


@router.get('/details')
@router.renders('task/single')
def taskDetails(req, resp):
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)

    if task and not task.value:
        # Not a leaf node, so we show the search results instead
        search = task.key + ':'
        result = UseCase.forWeb(req, TaskListUseCase).filter(search)
        result.update({
            "title": search + '*',
            "search": search,
            "toolbar": "partials/toolbar/list.html",
        })
        return router.render_template('list.html', result)

    # Show the task view
    view = UseCase.forWeb(req, TaskDetailUseCase)
    return view.index(task)


@router.get('/history')
@router.renders('task/history')
def taskRunHistory(req, resp):
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    view = UseCase.forWeb(req, TaskDetailUseCase)
    return view.history(task)


@router.get('/dep-graph')
@router.renders('task/dep-graph')
def taskDependencyGraph(req, resp):
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    view = UseCase.forWeb(req, TaskDetailUseCase)
    return view.graph(task)
