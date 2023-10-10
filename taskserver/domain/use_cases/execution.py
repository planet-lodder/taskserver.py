from taskserver.domain.entities.Task import Task
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig


class TaskExecutionUseCase(TaskfileUseCase):

    def find(self, task_name: str) -> Task:
        return self.root.find(task_name)

    def breakdown(self, task: Task):
        breakdown = []

        if task and self.taskfile:
            # Not a leaf node, so show the search results instead
            config = TaskfileConfig.resolve(self.location)
            breakdown = config.breakdown(task.key)

        # Show the task view
        return {
            "task": task,
            "taskfile": self.taskfile,
            "breakdown": breakdown,
        }
