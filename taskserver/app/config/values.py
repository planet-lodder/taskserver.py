from taskserver import router
from taskserver.domain.handlers.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import HtmxRequest


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


class ValueChangedInput(WebSerializer):
    def parse(self):
        return self.forTarget("env")

    def forTarget(self, dest):
        htmx = HtmxRequest(self.req)

        # Resolve key for value that changed
        key = htmx.prompt or ""
        if not key and htmx.triggerName:
            key = htmx.triggerName[len(f'config.{dest}.'):]

        # Get the key value
        value = "" if not key else htmx.input(f'config.{dest}.{key}') or ""

        # Return relevant information
        return dest, key, value

    def forDelete(self, dest):
        htmx = HtmxRequest(self.req)
        key = htmx.triggerName
        return dest, key


@router.post('/config/env')
@router.renders("partials/values/item")
def taskEditConfigEnv(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ValueChangedInput)
    dest, key, value = input.forTarget("env")
    return view.updateValue(dest, key, value)


@router.delete('/config/env')
def taskRemoveConfigEnv(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ValueChangedInput)
    dest, key = input.forDelete("env")
    view.removeValue(dest, key)
    return ""  # empty result


@router.post('/config/vars')
@router.renders("partials/values/item")
def taskAddConfigEnv(req, resp):
    return taskfile_value_update(req, resp, "vars")


@router.delete('/config/vars')
def taskRemoveConfigVars(req, resp):
    taskfile_value_remove(req, resp, "vars")
    return ""
