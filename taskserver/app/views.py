from taskserver import router, task_server
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.details import TaskDetailUseCase
from taskserver.domain.use_cases.list import TaskListUseCase
from taskserver.models.TaskNode import TaskNode
from taskserver.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())


@router.get('/details')
@router.renders('task/single')
def taskDetails(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    if task and not task.value:
        # Not a leaf node, so we show the search results instead
        result = view.list(task)
        return router.render_template('task/list.html', result)

    # Show the task view
    return view.index(task)


@router.get('/history')
@router.renders('task/history')
def taskRunHistory(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    return view.history(task)


@router.get('/dep-graph')
@router.renders('task/dep-graph')
def taskDependencyGraph(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    return view.graph(task)
