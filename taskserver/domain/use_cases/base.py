from abc import ABC, abstractmethod
from typing import Type, TypeVar

from anyserver import WebRequest
from taskserver.domain.entities.Task import Task
from taskserver.domain.repositories.base import ATaskfileRepository
from taskserver.domain.repositories.memory import InMemory, InMemoryTaskRepository


class ATaskfileUseCase(ABC):

    def __init__(self, repo: ATaskfileRepository):
        self.repo = repo

    @property
    def path(self) -> str:
        return self.repo._path


T = TypeVar("T", bound=ATaskfileUseCase)


class UseCase():
    default_path = "Taskfile.yaml"

    @staticmethod
    def repo(filename: str) -> ATaskfileRepository:
        repo = InMemory.TaskfileRepository(filename)
        return repo

    @staticmethod
    def forWeb(req: WebRequest, cls: Type[T]) -> T:
        # Resolve the current Taskfile path
        # It can be specified in request URL or body
        path = req.input("path")
        path = path or req.query.get("path")
        path = path or UseCase.default_path

        # Create use case for specified file
        repo = UseCase.repo(path)
        return cls(repo)

    @staticmethod
    def forFile(filename, cls: Type[T]) -> T:        
        repo = UseCase.repo(filename)
        return cls(repo)
