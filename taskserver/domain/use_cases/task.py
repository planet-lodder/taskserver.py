from taskserver.domain.entities.Task import Task
from taskserver.use_cases.base import AbstractTaskUseCase


class TaskUseCase(AbstractTaskUseCase):
    def __init__(self, task_repo):
        self.repo = task_repo

    def get_by_name(self, task_name):
        return self.repo.get_by_name(task_name)

    def insert(self, task: Task):
        return self.repo.insert(task)

    def update(self, task: Task):
        return self.repo.update(task)

    def delete(self, task_name):
        self.repo.delete(task_name)

    def list(self):
        return self.repo.list()