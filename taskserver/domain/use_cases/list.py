from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskListUseCase(TaskfileUseCase):

    def index(self):
        result = self.list()
        result.update({
            "title": "Show All",
            "toolbar": "partials/toolbar/list.html",
        })
        return result

    def list(self, values=None):
        values = values or self.repo.listTasks()
        return {
            "taskfile": self.taskfile,
            "list": values
        }

    def search(self, terms: str):
        found = self.repo.searchTasks(terms)
        return self.list(found)
