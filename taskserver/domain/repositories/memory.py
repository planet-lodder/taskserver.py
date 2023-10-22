
from typing import Dict, List, Optional, Sequence

from taskserver.domain.models.Task import Task, TaskBase
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.repositories.base import TaskfileRepository


class InMemoryTaskRepository(TaskfileRepository):
    taskfile: Taskfile
    tasks: List[Task]
    menu: TaskNode

    def __init__(self, filename: str):
        super().__init__(filename)

        # Get an in memory cache for the taskfile info
        self.taskfile = Taskfile.tryLoad(filename)
        self.tasks = Taskfile.listTasks(filename)

        # Keep track if all the task nodes
        self.menu = TaskNode(name='', path=filename)
        self.menu.populate(self.tasks)

    def listTasks(self) -> Sequence[Task]:
        return self.tasks

    def searchTasks(self, terms) -> Sequence[Task]:
        def matches(val, term):
            return term.lower() in val.lower()

        def search(task: Task):
            match_all = True
            if terms:
                # Search for each work in the terms given
                for term in terms.split(' '):
                    found = False
                    found = found or matches(task.name, term)
                    found = found or matches(task.desc, term)                    
                    match_all = match_all and found
            return match_all

        return self.tasks if not len(terms) else list(filter(search, self.tasks))

    def findTask(self, name) -> Optional[Task]:
        for task in filter(lambda t: t.name == name, self.tasks.items()):
            return task
        return None

    def getMenu(self, task_path: str = '') -> Optional[TaskNode]:
        if not task_path:
            return self.menu
        return self.menu.find(task_path)
