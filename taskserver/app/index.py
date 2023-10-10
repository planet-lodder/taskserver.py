from taskserver import router
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.list import TaskListUseCase


@router.get('')
@router.renders('task/list')
def taskMain(req, resp):
    view = UseCase.forWeb(req, TaskListUseCase)
    return view.index()
