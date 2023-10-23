
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence
from taskserver.domain.models.Task import Task

from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.Taskfile import Taskfile


class TaskfileRepository(ABC):
    taskfile: Taskfile

    def __init__(self, filename: str): ...

    @abstractmethod
    def getConfig(self) -> Taskfile: ...

    @abstractmethod
    def getConfigEdits(self) -> Taskfile: ...

    @abstractmethod
    def saveConfig(self) -> Taskfile: ...

    @abstractmethod
    def listTasks(self) -> Sequence[Task]: ...

    @abstractmethod
    def searchTasks(self, terms: str) -> Sequence[Task]: ...

    @abstractmethod
    def findTask(self, task_name: str) -> Optional[Task]: ...

    @abstractmethod
    def getMenu(self, task_path: str = '') -> Optional[TaskNode]: ...

