
from taskserver.domain.use_cases.base import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig


class TaskfileUseCase(TaskfileUseCase):
    _root = None

    @property
    def root(self):
        return self.repo.nodes

    @property
    def taskfile(self) -> TaskfileConfig:
        return self.repo.taskfile
