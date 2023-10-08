from taskserver import router, task_server
from taskserver.models.TaskfileConfig import taskfile_for


@router.get('/list')
@router.renders("list/index")
def taskList(req, resp):
    taskfile = {"_path": task_server.location}
    return {
        "taskfile": taskfile,
        "list": task_server.list()
    }


@router.post('/list')
@router.renders("list/index")
def taskSearch(req, resp):
    terms = "" if req.body and not "search" in req.body else req.body["search"]
    taskfile = {"_path": task_server.location}
    return {
        "taskfile": taskfile,
        "list": task_server.filter(terms)
    }
