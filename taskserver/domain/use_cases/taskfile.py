
from taskserver import task_server
from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.base import ATaskfileUseCase
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import TaskfileConfig


class TaskfileUseCase(ATaskfileUseCase):
    _root = None

    @property
    def root(self):
        if not self._root:
            self._root = TaskNode('', 'Task Actions')
            self._root.populate(task_server.list())
        return self._root

    @property
    def taskfile(self) -> TaskfileConfig:
        return self.repo.taskfile()
