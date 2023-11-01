
from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskSideNavUseCase(TaskfileUseCase):

    def index(self):
        result = self.defaults()
        result.update({
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",
        })
        return result

    def nodeInfo(self, key: str):
        result = self.defaults()
        result.update({"item": self.repo.getMenu(key)})
        return result

    def toggle(self, key: str):
        result = self.defaults()
        # Toggle the open state (show/hide children)
        if node := self.repo.getMenu(key):
            node.open = not node.open
            result.update({"item": node})
            return result

        raise Exception(f"No node could be found called {key}")
