
from anyserver import WebRequest

from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase


@router.get('/config')
@router.renders("task/config")
def taskConfig(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    return view.index(trigger_import=req.query.get('import'))


@router.post('/config')
@router.renders("task/config")
def taskUpdateConfig(req: WebRequest, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    values = req.inputs('config.', strip_prefix=True)
    return view.updatePartial(values)
