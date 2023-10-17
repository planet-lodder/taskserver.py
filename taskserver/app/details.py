from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.serializers.static import Serialize
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.details import TaskDetailUseCase


@router.get('/details')
@router.renders('task/single')
def taskDetails(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)

    # Show the task view if the selected node is a task
    if node and node.value:
        task = view.repo.findTask(node.key)
        print(f' -- [ {task} ]')
        return view.index(task)

    # Not a leaf (task) node, so we show the search results instead
    result = view.list(node)
    return router.render_template('task/list.html', result)


@router.get('/history')
@router.renders('task/history')
def taskRunHistory(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)
    return view.history(node)


@router.get('/dep-graph')
@router.renders('task/dep-graph')
def taskDependencyGraph(req, resp):
    view = UseCase.forWeb(req, TaskDetailUseCase)
    node = Serialize.fromWeb(req, TaskRequest).selected(view.repo)
    return view.graph(node)
