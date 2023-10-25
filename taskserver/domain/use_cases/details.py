
import yaml
from taskserver.domain.models.Task import Task
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.use_cases.list import TaskListUseCase
from taskserver.domain.use_cases.taskfile import TaskfileUseCase


class TaskDetailUseCase(TaskfileUseCase):

    def base(self, task: Task):
        # Load additional task details if needed (like interpolated vars)
        vars = self.repo.getTaskValues(task) if task else {}
        
        return {
            "taskfile": self.taskfile,
            "task": task,
            "vars": vars,
        }

    def index(self, task: Task):
        result = self.base(task)
        result.update({
            "toolbar": "partials/toolbar/task.html",
            "title": task.name if task else "(unknown)",
        })
        return result

    def list(self, task_prefix: str):
        search = task_prefix
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
            "title": f'{task.name} - Run History',
        })
        return result

    def graph(self, task: Task):
        result = self.base(task)
        result.update({
            "title": f'{task.name} - Dependency Graph',
        })
        return result
