from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.breakdown import TaskExecutionUseCase
from taskserver.utils import HtmxRequest

@router.get('/breakdown')
@router.renders('partials/execution/list')
def taskBreakdown(req, resp):
    view = UseCase.forWeb(req, TaskExecutionUseCase)
    htmx = HtmxRequest(req)
    task = view.find(htmx.triggerName)
    result = view.breakdown(task)
    return result
