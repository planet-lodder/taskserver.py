
from abc import ABC, abstractmethod
import os
from typing import Optional, Sequence

from taskserver.domain.entities.Task import Task
from taskserver.models.TaskfileConfig import TaskfileConfig


class ATaskfileRepository(ABC):

    def __init__(self, filename: str):
        self._filename = filename
        self._taskfile = None

    def taskfile(self):
        if not self._taskfile:
            self._taskfile = self.load()  # Load and cache result
        return self._taskfile

    def load(self):
        path = self._filename

        # Resolve the current taskfile
        if not os.path.exists(path):
            return TaskfileConfig.resolve(path)
        
        return {"_path": self._filename}

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
