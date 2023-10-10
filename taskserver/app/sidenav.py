from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.sidenav import TaskSideNavUseCase
from taskserver.utils import HtmxRequest


@router.get('/sidenav')
@router.renders('task/sidenav')
def taskMain(req, resp):
    view = UseCase.forWeb(req, TaskSideNavUseCase)
    return view.index()


@router.post('/sidenav/toggle')
@router.renders('partials/sidenav/menu-item')
def taskMain(req, resp):
    view = UseCase.forWeb(req, TaskSideNavUseCase)
    htmx = HtmxRequest(req)
    key = htmx.triggerName
    return view.toggle(key)
