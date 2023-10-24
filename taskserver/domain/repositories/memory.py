
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
        super().__init__(filename)  # Init base class
        # Get an in memory cache for the taskfile info
        self.taskfile = Taskfile(
            path=filename,
            includes={},
            version=3,
            env={},
            vars={},
            tasks={}
        )
        self.tasks = []
        self.menu = TaskNode(name='', path=filename)

    # Return cached taskfile
    def getConfig(self) -> Taskfile: return self.taskfile

    # Just return config (in-memory editing)
    def getConfigEdits(self) -> Taskfile: return self.getConfig()

    # Try and save the in-memory taskfile to disk
    def saveConfig(self, taskfile: Taskfile, reload=False) -> Taskfile:
        self.taskfile = taskfile
        return taskfile

    # List all available tasks in the in-memory cache
    def listTasks(self) -> Sequence[Task]: return self.tasks

    # Filter tasks on the search terms
    def searchTasks(self, terms) -> Sequence[Task]:
        # In-memory search, match on name or desc
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

    # Try and find a task from the current in-memory cache, or return None
    def findTask(self, name) -> Optional[Task]:
        found = filter(lambda t: t.name == name, self.tasks.items())
        return next(found, None)

    # Get the menu item associated with the task
    def getMenu(self, task_path: str = '') -> Optional[TaskNode]:
        return self.menu if not task_path else self.menu.find(task_path)
