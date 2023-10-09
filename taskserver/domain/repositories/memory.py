
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from taskserver.domain.entities.Task import Task
from taskserver.repo.base import AbstractTaskRepository

CACHED_TASKFILES = {}

class InMemoryTaskfile():
    tasks = []

    def add_task(self, task: Task):
        if found := filter(lambda t: t.name == task.name, self.tasks):
            raise Exception('Task already exists')
        item = task.dict()
        self.tasks.append(item)
        return item

    def find_task(self, task_name: str):
        if found := filter(lambda t: t.name == task_name, self.tasks):
            return list(found)[0]
        return None

    def update_task(self, task: Task):
        if item := self.find_task(task.name):
            item.update(task.dict())
            return item
        raise Exception('Cannot update task: not part of this taskfile.')

    @staticmethod
    def get(task: Task):
        file = "Taskfile.yaml"
        if not file in CACHED_TASKFILES:
            CACHED_TASKFILES[file] = {
                "version": 3,
                "tasks": []
            }
        return CACHED_TASKFILES[file]


class InMemoryTaskRepository(AbstractTaskRepository):

    def insert(self, task: Task) -> Optional[Task]:
        store = InMemoryTaskfile.get(task)
        item = store.add_task(task)
        return Task(**item)

    def update(self, task: Task) -> Task:
        store = InMemoryTaskfile.get(task)
        item = store.update_task(task)
        return Task(**item)

    def get_by_name(self, task_name) -> Optional[Task]:
        store = InMemoryTaskfile.get(None)
        if item := store.find_task(task_name):
            return Task(**item)
        else:
            return None

    def delete(self, task_name):
        store = InMemoryTaskfile.get(None)
        store.delete_task(task_name)

    def list(self) -> Optional[Sequence[Task]]:
        store = InMemoryTaskfile.get(None)
        tasks = store.tasks
        return [Task(**task) for task in tasks]
