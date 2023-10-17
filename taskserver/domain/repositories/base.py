
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from taskserver.domain.entities.Task import Task


class ATaskfileRepository(ABC):

    def __init__(self, filename: str):
        self._path = filename

    @abstractmethod
    def listTasks(self) -> Sequence[Task]: ...

    @abstractmethod
    def searchTasks(self, terms) -> Sequence[Task]: ...

    @abstractmethod
    def findTask(self, name) -> Optional[Task]: ...
