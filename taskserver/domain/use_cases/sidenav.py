
from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskSideNavUseCase(TaskfileUseCase):

    def index(self):
        result = self.defaults()
        result.update({
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",            
        })
        return result

    def toggle(self, key: str):
        # Toggle the open state (show/hide children)
        if node := self.repo.getMenu(key):
            node.open = not node.open
            return {"item": node}
        raise Exception(f"No node could be found called {key}")
