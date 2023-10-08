from taskserver import router, task_server
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())

@router.get('/breakdown')
@router.renders('execution/list')
def taskSummary(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)
    task = root.find(htmx.triggerName)
    breakdown = []

    if task and taskfile:
        # Not a leaf node, so show the search results instead
        breakdown = taskfile.breakdown(task.key)
    
    # Show the task view
    return {
        "task": task,
        "taskfile": taskfile,
        "breakdown": breakdown,
    }
