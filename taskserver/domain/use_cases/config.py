import random
import string
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig
from taskserver.models.TaskfileInclude import TaskfileInclude

HINT_EMPTY_VALUE = "Enter path to Taskfile.yaml or directory containing one"


def _new_id():  # Pseudo random id, to track this edit session
    return "_new_" + ''.join(random.choice(string.ascii_letters) for i in range(10))


class TaskConfigUseCase(TaskfileUseCase):

    def index(self):
        result = {
            "title": "Configuration",
            "toolbar": "partials/toolbar/config.html",
            "taskfile": self.taskfile
        }
        return result

    def getInclude(self, key, value):
        result = {
            "key": key or "",
            "value": value or "",
            "taskfile": self.taskfile,
        }
        return result

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

    def updateInclude(self, id, key, value):
        # Validate inputs for the given taskfile include
        taskfile = self.taskfile
        errors = TaskfileInclude(taskfile, key, value).validate(key, value)
        changed = False
        focus = f'key_{id}' if not key else f'value_{id}'

        if key and not key == id:
            if key in self.taskfile.includes:
                # Key is already defined, fail validation
                errors['key'] = [] if not 'key' in errors else errors['key']
                errors['key'].append('Key with this name already exists')
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
            "placeholder": value or HINT_EMPTY_VALUE,
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
        taskfile = TaskfileConfig.resolve(self.location)
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

        print(f'Update config.{dest}: {taskfile._path}')
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
