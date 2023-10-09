
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from taskserver.domain.entities.Task import Task
from taskserver.repo.base import AbstractTaskRepository


class FilesystemTaskRepository(AbstractTaskRepository):
    @abstractmethod
    def insert(self, task: Task) -> Optional[Task]:
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    def get_by_name(self, task_name) -> Optional[Task]:
        pass

    @abstractmethod
    def delete(self, task_name):
        pass

    @abstractmethod
    def list(self) -> Optional[Sequence[Task]]:
        pass
