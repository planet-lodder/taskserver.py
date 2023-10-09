
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from taskserver.domain.entities.Task import Task
from taskserver.models.Task import Task as TaskModel
from taskserver.repo.base import AbstractTaskRepository


class InMemoryTaskRepository(AbstractTaskRepository):

    def insert(self, task: Task) -> Optional[Task]:
        item = TaskModel.objects.create(**task.dict())
        return Task(**item.__dict__)

    def update(self, task: Task) -> Task:
        TaskModel.objects.filter(name=task.name).update(**task.dict())
        updated = TaskModel.objects.get(name=task.name)
        return Task(**updated.__dict__)

    def get_by_name(self, task_name) -> Optional[Task]:
        if task := TaskModel.objects.filter(name=task_name).first():
            return Task(**task.__dict__)
        else:
            return None

    def delete(self, task_name):
        TaskModel.objects.get(name=task_name).delete()

    def list(self) -> Optional[Sequence[Task]]:
        tasks = TaskModel.objects.all()
        return [Task(**task.__dict__) for task in tasks]
