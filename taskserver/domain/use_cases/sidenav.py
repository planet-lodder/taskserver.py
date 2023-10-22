
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskSideNavUseCase(TaskfileUseCase):

    def index(self):
        menu = self.repo.getMenu()
        result = {
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",
            "taskfile": self.taskfile,
            "menu": menu,
        }
        return result

    def toggle(self, key: str):
        # Toggle the open state (show/hide children)
        if node := self.repo.getMenu(key):
            node.open = not node.open
            return {"item": node}
        raise Exception(f"No node could be found called {key}")
