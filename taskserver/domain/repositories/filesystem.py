
from typing import Optional, Sequence
from taskserver.domain.models.Task import Task
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.TaskSummary import TaskSummary
from taskserver.domain.models.Taskfile import Taskfile

from taskserver.domain.repositories.base import TaskfileRepository
from taskserver.models.TaskfileConfig import TaskfileConfig


class FilesystemTaskfileRepo(TaskfileRepository):

    def __init__(self, filename: str):
        super().__init__(filename)

        # Load the taskfile list of tasks into memory
        self.taskfile = Taskfile.tryLoad(filename)
        self.tasks = Taskfile.listTasks(filename)

        # Generate the node list for the side navigation
        self.nodes = TaskNode(path=filename, name='')
        self.nodes.populate(self.tasks)

    def listTasks(self) -> Sequence[TaskSummary]:
        return self.tasks

    def searchTasks(self, terms) -> Sequence[TaskSummary]:
        def matches(val, term):
            return term.lower() in val.lower()

        def search(task):
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
        for task in filter(lambda t: t.name == name, self.tasks):
            print(f'Found [{name}]: {task}')
            return task
        return None

    def getMenu(self, task_path: str = '') -> Optional[TaskNode]:
        if not task_path:
            return self.nodes
        return self.nodes.find(task_path)
