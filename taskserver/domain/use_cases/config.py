from taskserver.main import task_server

from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskConfigUseCase(TaskfileUseCase):

    def index(self):
        result = self.list()
        result.update({
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",
        })
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

    def removeValue(self, dest, key):
        if not key:
            raise Exception("Expected 'hx-trigger-name' header.")

        taskfile = self.taskfile
        if dest in taskfile and key in taskfile[dest]:
            del taskfile[dest][key]

