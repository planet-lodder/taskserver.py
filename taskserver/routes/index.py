import os

from taskserver import router, task_server


@router.get('')
@router.renders('task/list')
def taskMain(req, resp):
    # TODO: Load from resolver
    # taskfile = taskfile_for(req)
    taskfile = {"_path": task_server.location}
    res = {
        "title": "Show All",
        "toolbar": "task/toolbar/list.html",
        "taskfile": taskfile,
        "list": task_server.list()
    }
    return res
