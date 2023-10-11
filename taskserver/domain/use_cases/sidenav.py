
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskSideNavUseCase(TaskfileUseCase):

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
