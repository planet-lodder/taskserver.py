import os
import random
import string
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig

HINT_EMPTY_VALUE = "Enter path to Taskfile.yaml or directory containing one"


def _new_id():  # Pseudo random id, to track this edit session
    return "_new_" + ''.join(random.choice(string.ascii_letters) for i in range(10))


class TaskConfigUseCase(TaskfileUseCase):

    def index(self, trigger_import=False):
        return {
            "title": "Configuration",
            "toolbar": "partials/toolbar/config.html",
            "taskfile": self.taskfile,
            "trigger_import": trigger_import
        }

    def getInclude(self, key, value):
        if not value and key in self.taskfile.includes:
            # Load current value from config
            value = self.taskfile.includes[key]

        return {
            "key": key or "",
            "value": value or "",
            "taskfile": self.taskfile,
        }

    def newInclude(self, key, value):
        id = key or _new_id()
        hint = value if value and key else HINT_EMPTY_VALUE
        focus = f'key_{id}' if not key else f'value_{id}'
        return {
            "id": id,
            "key": key or "",
            "value": value or "",
            "taskfile": self.taskfile,
            "autofocus": focus,
            "placeholder": hint,
        }

    def validateInclude(self, old_key, key, value):
        errors = {}

        def error(key, message):
            errors[key] = errors[key] if key in errors else []
            errors[key].append(message)

        if not key:
            # Key is required
            error("key", "Key name is required")

        if not value:
            # Value is required
            error("value", "Value is required")

        if len(errors.keys()):
            # Basic validation failed, no need to run additional checks
            return errors

        if key and not key == old_key:
            if key in self.taskfile.includes:
                # Key is already defined, fail validation
                error("key", 'Key with this name already exists')

        # Check that the path exists
        basepath = os.path.dirname(self.taskfile._path)
        filepath = os.path.join(basepath, value)
        if not os.path.exists(filepath):
            # File or folder does not exists
            error("value", "File or folder path does not point to a taskfile")

        if os.path.isdir(filepath) and not os.path.isfile(filepath + "Taskfile.yaml"):
            # Cannot find a valid taskfile
            error(
                "value", f"Cannot resolve `{filepath}Taskfile.yaml` to a valid file.")

        return errors

    def updateInclude(self, id, key, value):
        # Validate inputs for the given taskfile include
        errors = self.validateInclude(id, key, value)
        changed = False
        focus = f'key_{id}' if not key else f'value_{id}'

        if key != id:
            if errors.get('key'):
                # Key validation vailed
                focus = f'key_{id}'

            elif id in self.taskfile.includes:
                print(f' * RENAME [ {id} -> {key} ] == {value}')

                # We are renaming an existing item, so delete the old entry
                self.taskfile.includes[key] = self.taskfile.includes[id]
                del self.taskfile.includes[id]

                # Save the key as the new id
                focus = f'value_{key}'
                id = key

        # Check for any validation errors
        if not len(errors):
            # Only update the value if it changed
            changed = not key in self.taskfile.includes  # is new entry?
            changed = changed or self.taskfile.includes[key] != value
            if changed:
                print(f' * INCLUDES [ {key} ] == {value}')
                self.taskfile.includes[key] = value

        # Return the current state values
        return {
            "id": id,
            "key": key or "",
            "value": value or "",
            "taskfile": self.taskfile,
            "placeholder": HINT_EMPTY_VALUE,
            "autofocus": focus,
            "errors": errors,
        }

    def deleteInclude(self, key):
        if not key:
            raise Exception("Expected 'include' key name.")

        taskfile = self.taskfile
        if key in taskfile.includes:
            del taskfile.includes[key]  # Soft delete the value from memory

    def updatePartial(self, values):
        taskfile = TaskfileConfig.resolve(self.path)
        taskfile.update(values)
        taskfile.save(reload=True)
        result = {
            "title": "Configuration",
            "toolbar": "partials/toolbar/config.html",
            "taskfile": taskfile,
        }
        return result

    def updateValue(self, dest, key, value):
        taskfile = self.taskfile

        print(f'Update config.{dest}: {taskfile.path}')
        print(f' --> config[{dest}][{key}] == {value}')

        values = taskfile[dest] = taskfile[dest] if dest in taskfile else {}
        if not key in values or not value == values[key]:
            # Update the value that is stored in memory
            values[key] = value

        result = {
            "dest": dest,
            "key": key,
            "value": value,
            "focus": True,
            "taskfile": taskfile,
            "placeholder": "Enter value here",
        }

        return result

    def deleteValue(self, dest, key):
        if not key:
            raise Exception("Expected 'hx-trigger-name' header.")

        taskfile = self.taskfile
        if dest in taskfile and key in taskfile[dest]:
            del taskfile[dest][key]
