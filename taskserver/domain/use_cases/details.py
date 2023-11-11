
import yaml
from taskserver.domain.models.Task import Task
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.use_cases.list import TaskListUseCase
from taskserver.domain.use_cases.base import TaskfileUseCase
from taskserver.domain.use_cases.task import TaskUseCase


class TaskDetailUseCase(TaskUseCase):

    def index(self, task: Task, values=None):
        vars = self.getRunVars(task)
        selected = None
        for key in values or {}:
            val = values[key]
            if not selected and val != vars[key]:
                selected = key
            vars[key] = val

        result = self.base(task)
        result.update({
            "toolbar": "partials/toolbar/task.html",
            "title": task.name if task else "(unknown)",
            "selected": selected,
        })
        return result

    def list(self, task_prefix: str):
        search = task_prefix
        result = TaskListUseCase(self.repo, self.session).search(search)
        result.update({
            "title": search + '(list)',
            "search": search,
            "toolbar": "partials/toolbar/list.html",
        })
        return result

    def history(self, task: Task):
        result = self.base(task)
        result.update({
            "title": f'{task.name} - Run History',
        })
        return result

    def graph(self, task: Task):
        result = self.base(task)
        result.update({
            "title": f'{task.name} - Dependency Graph',
        })
        return result
