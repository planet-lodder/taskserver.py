from abc import ABC, abstractmethod
from typing import Type, TypeVar

from taskserver.domain.entities.Task import Task
from taskserver.domain.repositories.base import ATaskfileRepository
from taskserver.domain.repositories.memory import InMemoryTaskRepository


class ATaskfileUseCase(ABC):

    def __init__(self, repo: ATaskfileRepository):
        self.repo = repo


T = TypeVar("T", bound=ATaskfileUseCase)


class UseCase():
    default_path = "Taskfile.yaml"

    @staticmethod
    def forWeb(req, cls: Type[T]) -> T:
        # Resolve the current Taskfile path, if specified in request object
        path = req.body["location"] if req and req.body and "location" in req.body else None
        return UseCase.forFile(path or UseCase.default_path, cls)

    @staticmethod
    def forFile(filename, cls: Type[T]) -> T:
        repo = InMemoryTaskRepository(filename)
        res = cls(repo)
        return res
