
from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.list import TaskListUseCase
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskDetailUseCase(TaskfileUseCase):

    def base(self, task: Task):
        return {
            "taskfile": self.taskfile,
            "task": task,
        }

    def index(self, task: Task):
        result = self.base(task)
        result.update({
            "toolbar": "partials/toolbar/task.html",
            "title": task.key if task else "(unknown)",
        })
        return result

    def list(self, task: Task):
        search = task.key + ':'
        result = TaskListUseCase(self.repo).search(search)
        result.update({
            "title": search + '(list)',
            "search": search,
            "toolbar": "partials/toolbar/list.html",
        })
        return result

    def history(self, task: Task):
        result = self.base(task)
        result.update({
            "title": f'{task.key} - Run History',
        })
        return result

    def graph(self, task: Task):
        result = self.base(task)
        result.update({
            "title": f'{task.key} - Dependency Graph',
        })
        return result
