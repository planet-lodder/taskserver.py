from taskserver import router, task_server
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.list import TaskListUseCase
from taskserver.models.TaskfileConfig import taskfile_for


@router.get('/list')
@router.renders("partials/list/index")
def taskList(req, resp):
    store = UseCase.forWeb(req, TaskListUseCase)
    return {
        "taskfile": store.taskfile,
        "list": store.list()
    }


@router.post('/list')
@router.renders("partials/list/index")
def taskSearch(req, resp):
    store = UseCase.forWeb(req, TaskListUseCase)
    
    # task = Serializer.TaskCreate(request).entity(required=True)
    terms = "" if req.body and not "search" in req.body else req.body["search"]

    return {
        "taskfile": store.taskfile,
        "list": store.filter(terms)
    }
