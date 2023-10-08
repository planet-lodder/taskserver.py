from backend.task import router, taskserver
from backend.task.models.TaskfileConfig import taskfile_for


@router.get('/list')
@router.renders("task/list/index")
def taskList(req, resp):
    taskfile = {"_path": taskserver.location}
    return {
        "taskfile": taskfile,
        "list": taskserver.list()
    }


@router.post('/list')
@router.renders("task/list/index")
def taskSearch(req, resp):
    terms = "" if req.body and not "search" in req.body else req.body["search"]
    taskfile = {"_path": taskserver.location}
    return {
        "taskfile": taskfile,
        "list": taskserver.filter(terms)
    }
