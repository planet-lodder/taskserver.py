from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.serializers.core import Serialize
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.details import TaskDetailUseCase


@router.get('/task')
@router.renders('task/single')
def taskDetails(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)

    # Show the task view if the selected node is a task
    if node and node.data:
        return view.index(node.data)

    # Not a leaf (task) node, so we show the search results instead
    result = view.list(node.name + ':')
    return router.render_template('task/list.html', result)

@router.post('/task')
@router.renders('task/single')
def taskEditDetails(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)

    # Show the task view if the selected node is a task
    if node and node.data:
        vars = req.inputs('config.task.', strip_prefix=True)
        return view.index(node.data, vars)

    return taskDetails(req, resp)


@router.get('/history')
@router.renders('task/history')
def taskRunHistory(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)
    return view.history(node.data)


@router.get('/dep-graph')
@router.renders('task/dep-graph')
def taskDependencyGraph(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)
    return view.graph(node.data)
