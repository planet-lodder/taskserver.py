
import os

import yaml
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskfileUseCase(TaskfileUseCase):

    @property
    def taskfile(self) -> Taskfile:
        return self.repo.taskfile

