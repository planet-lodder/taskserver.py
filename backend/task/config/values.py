from backend.task import router
from backend.task.models.TaskfileConfig import taskfile_for
from backend.task.utils import HtmxRequest


def taskfile_value_update(req, resp, dest):
    htmx = HtmxRequest(req)
    taskfile = taskfile_for(req)

    # Resolve the key name from the known trigger or prompt
    key = htmx.prompt or ""
    if not key and htmx.triggerName:
        key = htmx.triggerName[len(f'config.{dest}.'):]

    value = "" if not key else htmx.input(f'config.{dest}.{key}') or ""

    print(f'Update config.{dest}: {taskfile._path}')
    print(f' --> config[{dest}][{key}] == {value}')
    values = taskfile[dest] = taskfile[dest] if dest in taskfile else {}
    if not key in values or not value == values[key]:
        # Update the value that is stored in memory
        values[key] = value

    data = {
        "dest": dest,
        "key": key,
        "value": value,
        "focus": True,
        "taskfile": taskfile,
        "placeholder": "Enter new value here",
    }

    return data


def taskfile_value_remove(req, resp, dest):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)
    key = htmx.triggerName
    
    if not key:
        raise Exception("Expected 'hx-trigger-name' header.")
    if dest in taskfile and key in taskfile[dest]:
        del taskfile[dest][key]

    return taskfile


@router.post('/config/env')
@router.renders("task/values/item")
def taskAddConfigEnv(req, resp):
    return taskfile_value_update(req, resp, "env")


@router.delete('/config/env')
def taskRemoveConfigEnv(req, resp):
    taskfile_value_remove(req, resp, "env")
    return ""


@router.post('/config/vars')
@router.renders("task/values/item")
def taskAddConfigEnv(req, resp):
    return taskfile_value_update(req, resp, "vars")


@router.delete('/config/vars')
def taskRemoveConfigVars(req, resp):
    taskfile_value_remove(req, resp, "vars")
    return ""
