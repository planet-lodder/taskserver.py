
from abc import ABC, abstractmethod
from asyncio import Task
from typing import Dict, List, Optional, Sequence

from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.Taskfile import Taskfile


class TaskfileRepository(ABC):
    taskfile: Taskfile

    _path: str

    def __init__(self, filename: str):
        self._path = filename

    @abstractmethod
    def listTasks(self) -> Sequence[Task]: ...

    @abstractmethod
    def searchTasks(self, terms: str) -> Sequence[Task]: ...

    @abstractmethod
    def findTask(self, task_name: str) -> Optional[Task]: ...

    @abstractmethod
    def getMenu(self, task_path: str = '') -> Optional[TaskNode]: ...
