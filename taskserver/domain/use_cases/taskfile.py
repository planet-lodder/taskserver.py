
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskfileUseCase(TaskfileUseCase):
    _root = None

    @property
    def root(self):
        return self.repo.nodes

    @property
    def taskfile(self) -> Taskfile:
        return self.repo.taskfile
