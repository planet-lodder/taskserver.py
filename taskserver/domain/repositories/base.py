
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from taskserver.domain.entities.Task import Task


class TaskfileRepository(ABC):

    def __init__(self, filename: str):
        self._path = filename

    @abstractmethod
    def listTasks(self) -> Sequence[Task]: ...

    @abstractmethod
    def searchTasks(self, terms: str) -> Sequence[Task]: ...

    @abstractmethod
    def findTask(self, task_name: str) -> Optional[Task]: ...

    @abstractmethod
    def getStatus(self, task_name: str) -> Optional[TaskStatus]: ...
