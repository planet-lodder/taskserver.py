
from copy import deepcopy
import json
import os
from typing import List, Optional, Sequence
from taskserver.domain.models.Task import Task
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.repositories.base import TaskfileRepository


class FilesystemTaskfileRepo(TaskfileRepository):
    # Internal variables
    taskfile: Taskfile = None
    tasks: List[Task] = None
    edits: Taskfile = None  # Keep track of changed values
    menu: TaskNode = None

    def __init__(self, filename: str):
        super().__init__(filename)

        # Load the taskfile into memory
        self.taskfile = self.tryLoadTaskfile(filename)

    # Try and load existing taskfile (if it exists)

    def tryLoadTaskfile(self, path) -> Taskfile:
        try:
            return Taskfile.load(path)
        except:
            # Load empty taskfile if not found on disk
            return Taskfile(path=path, includes={}, version=3, env={}, vars={}, tasks={})

    # Return the cached taskfile config
    def getConfig(self) -> Taskfile: return self.taskfile

    # Create a copy of the originals, for editing
    def getConfigEdits(self) -> Taskfile:
        self.edits = self.edits or deepcopy(self.taskfile)
        return self.edits

    def saveConfig(self, taskfile: Taskfile, reload=False) -> Taskfile:

        # After saving the taskfile, update the local caches
        self.taskfile = Taskfile.load(taskfile.path) if reload else taskfile
        self.edits = None

        return self.taskfile

    def listTasks(self) -> Sequence[Task]:
        if self.tasks:
            return self.tasks  # Use cached list of tasks
        try:
            # No cached list of tasks, so we go discover them
            taskfile = self.taskfile

            # Run: task --list-all --json
            output, err, res = Taskfile.run(taskfile.path, '--list-all --json')

            # Parse the JSON into a list of tasks
            obj = json.loads(output)

            # Parse the items into a list
            list = obj.get("tasks", [])
            path = obj.get("location", "")
            base = os.path.dirname(path) if path else os.getcwd()
            tasks = []
            for item in list:
                # Update and normalize paths for all tasks by stripping base folder prefix
                loc = item.get("location", {})
                path = loc.get("taskfile", '')
                path = path.removeprefix(base + "/")
                task = Task(
                    path=path,
                    name=item.get("name"),
                    desc=item.get("desc"),
                    up_to_date=bool(item.get('up_to_date', False)),
                )
                tasks.append(task)

            # Save ref to the new list of parse tasks
            self.tasks = tasks

            return tasks
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {taskfile.path}.')

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
                    match_all = match_all and found
            return match_all

        tasks = self.listTasks()  # Get the list of tasks to filter
        return tasks if not len(terms) else list(filter(search, tasks))

    def findTask(self, name) -> Optional[Task]:
        for task in filter(lambda t: t.name == name, self.listTasks()):
            return task
        return None

    def getMenu(self, task_path: str = '') -> Optional[TaskNode]:
        if not self.menu:
            # Generate the node list for the side navigation
            self.menu = TaskNode(path=self.taskfile.path, name='')
            self.menu.populate(self.listTasks())
        if not task_path:
            # Return the root node
            return self.menu
        # Search for the node by task path
        return self.menu.find(task_path)
