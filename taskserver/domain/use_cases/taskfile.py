from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.base import ATaskfileUseCase


class TaskfileUseCase(ATaskfileUseCase):

    @property
    def taskfile(self):
        return self.repo.taskfile()
