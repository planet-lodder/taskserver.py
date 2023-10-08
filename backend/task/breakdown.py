from backend.task import router, taskserver
from backend.task.models.TaskNode import TaskNode
from backend.task.models.TaskfileConfig import taskfile_for
from backend.task.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(taskserver.list())

@router.get('/breakdown')
@router.renders('task/execution/list')
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
