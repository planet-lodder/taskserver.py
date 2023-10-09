
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from taskserver.domain.entities.Task import Task


class AbstractTaskRepository(ABC):
    @abstractmethod
    def insert(self, task: Task) -> Optional[Task]:
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        ...

    @abstractmethod
    def get_by_name(self, task_name) -> Optional[Task]:
        ...

    @abstractmethod
    def delete(self, task_name):
        ...

    @abstractmethod
    def list(self) -> Optional[Sequence[Task]]:
        ...
