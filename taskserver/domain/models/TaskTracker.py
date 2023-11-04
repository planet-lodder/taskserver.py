
from typing import List
from abc import ABC, abstractmethod

from taskserver.domain.models.TaskCommand import Command, TaskCommand


class TaskTracker(ABC):
    @abstractmethod
    def setOverflow(self, parent: Command, overflow: str): ...

    @abstractmethod
    def cmdStarted(self, stack: List[TaskCommand],
                   cmd_raw: str, up_to_date: bool = None): ...

    @abstractmethod
    def taskStarted(self, stack: List[TaskCommand],
                    cmd_name: str, up_to_date: bool = None): ...

    @abstractmethod
    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    @abstractmethod
    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    @abstractmethod
    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand): ...
