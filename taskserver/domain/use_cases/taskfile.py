
from taskserver.domain.use_cases.base import ATaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig


class TaskfileUseCase(ATaskfileUseCase):
    _root = None

    @property
    def root(self):
        return self.repo.nodes

    @property
    def taskfile(self) -> TaskfileConfig:
        return self.repo.taskfile
