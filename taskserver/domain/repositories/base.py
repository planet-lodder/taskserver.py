
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence
from taskserver.domain.models.Task import Task, TaskVars

from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.TaskRun import TaskRun
from taskserver.domain.models.Taskfile import Taskfile


class TaskfileRepository(ABC):
    taskfile: Taskfile

    def __init__(self, filename: str): ...

    @abstractmethod
    def getConfig(self) -> Taskfile: ...

    @abstractmethod
    def getConfigEdits(self) -> Taskfile: ...

    @abstractmethod
    def saveConfig(self, taskfile: Taskfile, reload=False) -> Taskfile: ...

    @abstractmethod
    def listTasks(self) -> Sequence[Task]: ...

    @abstractmethod
    def searchTasks(self, terms: str) -> Sequence[Task]: ...

    @abstractmethod
    def findTask(self, task_name: str) -> Optional[Task]: ...

    @abstractmethod
    def getTaskValues(self, task: Task) -> TaskVars: ...

    @abstractmethod
    def getMenu(self, task_path: str = '') -> Optional[TaskNode]: ...

    @abstractmethod
    def startTaskRun(self, run: TaskRun) -> Optional[TaskRun]: ...

    @abstractmethod
    def getTaskRun(self, id: str) -> Optional[TaskRun]: ...
    
    @abstractmethod
    def saveTaskRun(self, run: TaskRun): ...
