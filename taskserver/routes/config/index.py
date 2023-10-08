
from taskserver import router
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import partial_values


@router.get('/config')
@router.renders("task/config/index")
def taskConfig(req, resp):
    taskfile = taskfile_for(req)
    data = {
        "title": "Configuration",
        "toolbar": "task/toolbar/config.html",
        "taskfile": taskfile
    }
    return data


@router.post('/config')
@router.renders("task/config/index")
def taskUpdateConfig(req, resp):
    partials = partial_values(req.body, "config.")
    taskfile = taskfile_for(req)
    taskfile.update(partials)
    taskfile.save(reload=True)

    data = {
        "title": "Configuration",
        "toolbar": "task/toolbar/config.html",
        "taskfile": taskfile,
    }
    return data
