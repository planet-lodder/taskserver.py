from taskserver.main import task_server

from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig


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
            "key": key,
            "value": value,
            "taskfile": self.taskfile,
        }
        return result

    def newInclude(self, id, key, value):
        hint = value if value and key else "Enter new value here"
        focus = f'key.includes.{id}' if not key else f'config.includes.{key}'
        return {
            "id": id,
            "key": key,
            "value": value,
            "taskfile": self.taskfile,
            "autofocus": focus,
            "placeholder": hint,
        }

    def updateInclude(self, id, key, value, hint, errors):
        focus = f'key.includes.{id}' if not key else f'config.includes.{id}'
        result = {
            "id": id,
            "key": key,
            "value": value,
            "taskfile": self.taskfile,
            "autofocus": focus,
            "placeholder": hint,
            "errors": errors,
        }

        # Check if the value should be updated (in the cache)
        if not key in self.taskfile.includes or value != self.taskfile.includes[key]:
            # Update they value from the input field
            print(f' * INCLUDES [ {key} ] == {value}')
            self.taskfile.includes[key] = value

        return result

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
