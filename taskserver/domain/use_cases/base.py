from abc import ABC, abstractmethod
from typing import Type, TypeVar

from taskserver.domain.entities.Task import Task
from taskserver.domain.repositories.base import ATaskfileRepository
from taskserver.domain.repositories.memory import InMemoryTaskRepository


class ATaskfileUseCase(ABC):

    def __init__(self, repo: ATaskfileRepository):
        self.repo = repo

    @property
    def location(self) -> str:
        return self.repo._path


T = TypeVar("T", bound=ATaskfileUseCase)


class UseCase():
    default_path = "Taskfile.yaml"

    @staticmethod
    def forWeb(req, cls: Type[T]) -> T:
        # Resolve the current Taskfile path, if specified in request object
        body = req.body if req and req.body else {}
        path = body["location"] if "location" in body else None
        path = path or UseCase.default_path
        repo = InMemoryTaskRepository.resolve(path)
        res = cls(repo)
        return res

    @staticmethod
    def forFile(filename, cls: Type[T]) -> T:
        repo = InMemoryTaskRepository.resolve(filename)
        res = cls(repo)
        return res
