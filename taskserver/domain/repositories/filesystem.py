
from typing import Optional, Sequence
from taskserver.domain.models.Task import Task

from taskserver.domain.repositories.base import TaskfileRepository
from taskserver.models.TaskList import TaskList
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import TaskfileConfig


class FilesystemTaskfileRepo(TaskfileRepository):

    def __init__(self, filename: str):
        super().__init__(filename)
        self.taskfile = TaskfileConfig.resolve(filename)
        self.tasks = TaskList.discover(filename)
        self.nodes = TaskNode('', 'Task Actions', task_list=self.tasks)

    def listTasks(self) -> Sequence[Task]:
        return self.tasks

    def searchTasks(self, terms) -> Sequence[Task]:
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
            return task
        return None
