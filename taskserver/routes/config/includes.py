import os
import random
import string

from taskserver import router
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import HtmxRequest


class TaskfileInclude(dict):

    def __init__(self, taskfile, key, value, raw={}):
        self.id = key or self._new_id()  # Used for new items (without key name)
        self.key = key
        self.value = value
        self.taskfile = taskfile
        dict.__init__(self, **raw)

    def _new_id(self):
        letters = string.ascii_letters
        return "_new_" + ''.join(random.choice(letters) for i in range(10))

    def validate(self, key, value):
        errors = {}

        def error(key, message):
            errors[key] = errors[key] if key in errors else []
            errors[key].append(message)

        if not key:
            # Key is required
            error("key", "Key is required")

        if not value:
            # Value is required
            error("value", "Value is required")

        if len(errors.keys()):
            # Basic validation failed, no need to run additional checks
            return errors

        # Check that the path exists
        basepath = os.path.dirname(self.taskfile._path)
        filepath = os.path.join(basepath, value)
        if not os.path.exists(filepath):
            # File or folder does not exists
            error("value", "File or folder path does not point to a taskfile")

        if os.path.isdir(filepath) and not os.path.isfile(filepath + "Taskfile.yaml"):
            # Cannot find a valid taskfile
            error("value", f"Cannot resolve `{filepath}Taskfile.yaml` to a valid file.")

        return errors

    @staticmethod
    def resolve(taskfile, htmx):
        key = TaskfileInclude.findKey(taskfile, htmx)
        value = TaskfileInclude.findValue(taskfile, htmx, key) if key else ""
        return TaskfileInclude(taskfile, key, value)

    @staticmethod
    def findKey(taskfile, htmx):
        requested_key = htmx.prompt or htmx.triggerName
        if requested_key:
            # Return the requested key (eg: when using add/delete/edit/cancel)
            return requested_key

        # Resolve the key name from given inputs
        # Update key/value pairs (if changed)
        prefix = f'key.includes.'
        for input in htmx.inputs(prefix):
            k = input[len(prefix):]
            l = htmx.input(f'{prefix}{k}')
            v = htmx.input(f'config.includes.{k}')
            if k != l:
                print(f' * RENAME [ {k} -> {l} ] == {v}')
                if k in taskfile.includes:
                    del taskfile.includes[k]
                taskfile.includes[l] = v
                return l
            else:
                print(f' * FOUND  [ {k} ] == {v}')
                return k

    @staticmethod
    def findValue(taskfile, htmx, key):
        value = None
        if key and htmx:  # Update they value from the input field
            value = htmx.input(f'config.includes.{key}')
        if value == None:  # Try and fetch from cache
            value = taskfile.includes.get(key, "")
        return value


@router.get('/config/includes')
@router.renders("task/config/includes/items/default")
def taskInclude(req, resp):
    htmx = HtmxRequest(req)
    taskfile = taskfile_for(req)
    include = TaskfileInclude.resolve(taskfile, htmx)
    key = include.key or ""
    value = include.value or ""
    return {        
        "key": key,
        "value": value,
        "taskfile": taskfile,
    }


@router.put('/config/includes')
@router.renders("task/config/includes/items/edit")
def taskIncludeNew(req, resp):
    htmx = HtmxRequest(req)
    taskfile = taskfile_for(req)

    # Look for the key/value pair using user input
    include = TaskfileInclude.resolve(taskfile, htmx)
    id = include.id
    key = include.key or ""
    value = include.value or ""
    hint = value if value and include.key else "Enter new value here"
    focus = f'key.includes.{id}' if not key else f'config.includes.{id}'
    return {
        "id": id,
        "key": key,
        "value": value,
        "taskfile": taskfile,
        "autofocus": focus,
        "placeholder": hint,
    }


@router.post('/config/includes')
@router.renders("task/config/includes/items/edit")
def taskIncludeEdit(req, resp):
    htmx = HtmxRequest(req)
    taskfile = taskfile_for(req)

    # Look for the key/value pair using user input
    include = TaskfileInclude.resolve(taskfile, htmx)
    id = include.id
    key = include.key
    value = include.value
    action = htmx.triggerValue

    # Validate input and creaqte data context object
    errors = include.validate(key, value)
    valid = not len(errors.keys())
    hint = include.value if action != "add" else "Enter new value here"
    focus = f'key.includes.{id}' if not key else f'config.includes.{id}'

    # Set some additional metadata
    data = {
        "id": include.id,
        "key": key,
        "value": value,
        "taskfile": taskfile,
        "autofocus": focus,
        "placeholder": hint,
        "errors": errors,
    }

    # Check if the value should be updated (in the cache)
    if not key in taskfile.includes or value != taskfile.includes[key]:
        # Update they value from the input field
        print(f' * INCLUDES [ {key} ] == {value}')
        taskfile.includes[key] = value

    if not valid or action in ["edit", "add"]:
        # Keep in edit mode
        return data

    # Value has been updated successfully, show in default mode
    return router.render_template("task/config/includes/items/default.html", data)


@router.delete('/config/includes')
def taskIncludeDelete(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)
    key = htmx.triggerName

    if key in taskfile.includes:
        del taskfile.includes[key]  # Soft delete the value from memory
    elif not key:
        raise Exception("Expected 'hx-trigger-name' header.")

    return ""  # Return empty result (swap with original html content)
