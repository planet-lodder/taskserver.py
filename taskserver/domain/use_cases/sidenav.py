from taskserver.main import task_server

from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskNode import TaskNode


class TaskSideNavUseCase(TaskfileUseCase):
    _root = None

    @property
    def root(self):
        if not self._root:
            self._root = TaskNode('', 'Task Actions')
            self._root.populate(task_server.list())
        return self._root

    def index(self):
        result = {
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",
            "taskfile": self.taskfile,
            "menu": self.root,
        }
        return result

    def toggle(self, key: str):
        node = self.root.find(key)
        if node:
            node.open = not node.open
        return {
            "item": node,
        }
