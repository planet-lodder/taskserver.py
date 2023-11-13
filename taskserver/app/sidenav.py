from taskserver import router
from taskserver.domain.serializers.core import Serialize
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.sidenav import TaskSideNavUseCase


@router.get('/sidenav')
@router.renders('task/sidenav')
def taskMain(req, resp):
    view = UseCase.forWeb(req, TaskSideNavUseCase)
    return view.index()


@router.get('/sidenav/node')
@router.renders('partials/sidenav/task-node')
def taskNode(req, resp):
    view = UseCase.forWeb(req, TaskSideNavUseCase)
    input = Serialize.fromWeb(req, TaskRequest)
    return view.nodeInfo(input.name)


@router.post('/sidenav/toggle')
@router.renders('partials/sidenav/task-node')
def taskNodeToggle(req, resp):
    view = UseCase.forWeb(req, TaskSideNavUseCase)
    input = Serialize.fromWeb(req, TaskRequest)
    return view.toggle(input.name)
