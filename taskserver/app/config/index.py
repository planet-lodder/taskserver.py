
from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase
from taskserver.utils import partial_values


@router.get('/config')
@router.renders("task/config")
def taskConfig(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)    
    return view.index()


@router.post('/config')
@router.renders("task/config")
def taskUpdateConfig(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)    
    partials = partial_values(req.body, "config.")
    return view.updatePartial(partials)
