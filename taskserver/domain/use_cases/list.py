from taskserver.main import task_server

from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskListUseCase(TaskfileUseCase):
    
    def list(self):
        return task_server.list()

    def filter(self, terms: str):
        return task_server.filter(terms)
