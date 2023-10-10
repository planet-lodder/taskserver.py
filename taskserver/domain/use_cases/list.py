from taskserver.main import task_server

from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskListUseCase(TaskfileUseCase):

    def index(self):
        result = self.list()
        result.update({
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",
        })
        return result

    def list(self, values=None):
        values = values if values else task_server.list()
        return {
            "taskfile": self.taskfile,
            "list": values
        }

    def filter(self, terms: str):
        found = task_server.filter(terms)
        return self.list(found)
