from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase
from taskserver.models.TaskfileInclude import TaskfileInclude


class ConfigIncludeInputs(WebSerializer):

    def parse(self): return None

    def resolve(self, taskfile):
        key = self.findKey(taskfile)
        value = self.findValue(taskfile, key) if key else ""
        return TaskfileInclude(taskfile, key, value)

    def findKey(self, taskfile, htmx):
        htmx = self.htmx

        # Look for request originating from HTMX interactions
        # Return the requested key (eg: when using add/delete/edit/cancel)
        if htmx:
            if requested_key := htmx.prompt or htmx.triggerName:
                return requested_key

        # Resolve the key name from given inputs
        # Update key/value pairs (if changed)
        prefix = f'key.includes.'
        for k in self.req.inputs(prefix, strip_prefix=True):
            l = self.req.input(f'{prefix}{k}')
            v = self.req.input(f'config.includes.{k}')
            if k != l:
                print(f' * RENAME [ {k} -> {l} ] == {v}')
                if k in taskfile.includes:
                    del taskfile.includes[k]
                taskfile.includes[l] = v
                return l
            else:
                print(f' * FOUND  [ {k} ] == {v}')
                return k

    def findValue(self, taskfile, htmx, key):
        value = None
        if key and htmx:  # Update they value from the input field
            value = self.req.input(f'config.includes.{key}')
        if value == None:  # Try and fetch from cache
            value = taskfile.includes.get(key, "")
        return value


@router.get('/config/includes')
@router.renders("partials/config/includes/items/default")
def taskInclude(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    include = input.resolve(view.taskfile)
    return view.getInclude(include.key, include.value)


@router.put('/config/includes')
@router.renders("partials/config/includes/items/edit")
def taskIncludeAdd(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    include = input.resolve(view.taskfile)
    return view.newInclude(include.id, include.key, include.value)


@router.post('/config/includes')
@router.renders("partials/config/includes/items/edit")
def taskIncludeEdit(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    include = input.resolve(view.taskfile)

    id = include.id
    key = include.key
    value = include.value
    action = input.htmx.triggerValue
    hint = value if action != "add" else "Enter new value here"

    # Validate input and creaqte data context object
    errors = include.validate(key, value)
    valid = not len(errors.keys())
    result = view.updateInclude(id, key, value, hint, errors)

    # Keep in edit mode if not validated
    if not valid or action in ["edit", "add"]:
        return result
    else:
        # Value has been updated successfully
        return router.render_template("partials/config/includes/items/default.html", result)


@router.delete('/config/includes')
def taskIncludeDelete(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    key = input.htmx.triggerName
    view.deleteInclude(key)
    return ""  # empty result
