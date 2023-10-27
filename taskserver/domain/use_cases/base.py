from abc import ABC, abstractmethod
from typing import Dict, Type, TypeVar

from anyserver import WebRequest
from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.repositories import Repository
from taskserver.domain.repositories.base import TaskfileRepository

IN_MEMORY_SESSIONS = {}


class Session(dict):
    username: str
    runVars: Dict[str, TaskVars] = {}

    def __init__(self, username: str):
        self.username = username

    @classmethod
    def forUser(cls, username: str):
        if not username in IN_MEMORY_SESSIONS:
            IN_MEMORY_SESSIONS[username] = cls(username)
        return IN_MEMORY_SESSIONS[username]


class TaskfileUseCase(ABC):
    repo: TaskfileRepository
    session: Session

    def __init__(self, repo: TaskfileRepository, session: Session):
        self.repo = repo
        self.session = session

    @property
    def taskfile(self) -> Taskfile:
        return self.repo.taskfile

    def defaults(self):
        return {
            "taskfile": self.taskfile,
            "menu": self.repo.getMenu()
        }


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

        # Load the repository for the target Taskfile
        repo = Repository.forTaskfile(path)

        # TODO: Implement user-based sessions in the future
        session = Session.forUser('localhost')

        # Create use case for specified file
        return cls(repo, session)

    @staticmethod
    def forFile(filename, cls: Type[T]) -> T:
        repo = Repository.forTaskfile(filename)
        session = Session.forUser('localhost')  # Load from file as local user
        return cls(repo, session)
