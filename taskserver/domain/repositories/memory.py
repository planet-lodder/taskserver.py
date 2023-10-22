
from typing import Dict, List, Optional, Sequence
from taskserver.domain.models.Task import Task, TaskBase
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.TaskSummary import TaskSummary
from taskserver.domain.models.Taskfile import Taskfile

from taskserver.domain.repositories.base import TaskfileRepository
from taskserver.models.TaskfileConfig import TaskfileConfig


class InMemoryTaskRepository(TaskfileRepository):
    taskfile: Taskfile
    tasks: List[TaskSummary]
    menu: TaskNode

    def __init__(self, filename: str):
        super().__init__(filename)

        # Get an in memory cache for the taskfile info
        self.taskfile = Taskfile.tryLoad(filename)
        self.tasks = Taskfile.listTasks(filename)

        # Keep track if all the task nodes
        self.menu = TaskNode('', 'Task Actions', task_list=self.tasks)        

    def listTasks(self) -> Sequence[TaskSummary]:
        return self.tasks

    def searchTasks(self, terms) -> Sequence[TaskSummary]:
        def matches(val, term):
            return term.lower() in val.lower()

        def search(task: TaskSummary):
            match_all = True
            if terms:
                # Search for each work in the terms given
                for term in terms.split(' '):
                    found = False
                    found = found or matches(task.name, term)
                    found = found or matches(task.desc, term)
                    found = found or matches(task.summary, term)
                    match_all = match_all and found
            return match_all

        return self.tasks if not len(terms) else list(filter(search, self.tasks))

    def findTask(self, name) -> Optional[Task]:
        for task in filter(lambda t: t.name == name, self.tasks.items()):
            return task
        return None
