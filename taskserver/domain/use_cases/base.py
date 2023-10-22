from abc import ABC, abstractmethod
from typing import Type, TypeVar

from anyserver import WebRequest
from taskserver.domain.repositories import Repository
from taskserver.domain.repositories.base import TaskfileRepository


class TaskfileUseCase(ABC):

    def __init__(self, repo: TaskfileRepository):
        self.repo = repo


T = TypeVar("T", bound=TaskfileUseCase)


class UseCase():
    default_path = "Taskfile.yaml"

    @staticmethod
    def forWeb(req: WebRequest, cls: Type[T]) -> T:
        # Resolve the current Taskfile path
        # It can be specified in request URL or body
        path = req.input("path")
        path = path or req.query.get("path")
        path = path or UseCase.default_path

        # Create use case for specified file
        repo = Repository.forTaskfile(path)
        return cls(repo)

    @staticmethod
    def forFile(filename, cls: Type[T]) -> T:
        repo = Repository.forTaskfile(filename)
        return cls(repo)
