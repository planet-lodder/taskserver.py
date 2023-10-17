
# Todo: Implement task thread pool
from typing import List
from taskserver.domain.entities.Task import Task


TASK_THREADS = {
    "Taskfile.yaml": {
        "serve": [{"pid": 999}]
    }
}


class TaskNode():
    def __init__(self, key, name, value=None, state='', open=False, task_list=[]):
        self.key = key
        self.name = name
        self.value = value
        self.open = open
        self.state = state

        # Populate children if specified
        self.children = {}
        if len(task_list):
            self.populate(task_list)

    @property
    def path(self):
        if self.value and "location" in self.value:
            vals = self.value["location"]
            path = vals["taskfile"] if "taskfile" in vals else ""
            return path
        return ""

    @property
    def icon(self):
        task = self.value

        # Check for children
        if len(self.children.keys()):
            # Has children, so treat like a folder
            return 'icons/folder-minus.svg' if self.open else 'icons/folder-plus.svg'

        # Check the current state
        if "up_to_date" in task and task["up_to_date"]:
            return "icons/document-check.svg"
        elif "up_to_date" in task and not task["up_to_date"]:
            return "icons/document-text.svg"

        # Default icon
        return 'icons/document.svg'

    @property
    def style(self):
        task = self.value

        if self.key in TASK_THREADS["Taskfile.yaml"]:
            # Task is being executed or run
            return "text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-800 dark:hover:text-blue-200 hover:text-blue-700"

        # Check the current state
        if task and "up_to_date" in task and task["up_to_date"]:
            return "text-green-700 dark:text-green-300 hover:bg-green-100 dark:hover:bg-green-800 dark:hover:text-green-200 hover:text-green-700"

        # Default style
        return 'text-gray-600 dark:text-gray-300'

    @property
    def htmx(self):
        return f'name="{self.key}" hx-get="/task/details" hx-target="main"'

    @property
    def actions(self):
        task = self.value

        if self.key in TASK_THREADS["Taskfile.yaml"]:
            # Task is being executed or run
            return [
                {
                    "name": "Task Vars",
                    "icon": "icons/arrow-path.svg",
                    "href": "/task/start",
                    "style": "animate-spin"
                },
                {
                    "name": "Run Task",
                    "icon": "icons/stop.svg",
                    "href": "/task/build",
                    "style": "opacity-100"
                }
            ]

        if task:
            return [
                {
                    "name": "Task Vars",
                    "icon": "icons/list.svg",
                    "htmx": self.htmx
                },
                {
                    "name": "Run Task",
                    "icon": "icons/play.svg",
                    "htmx": f'name="{self.key}" hx-get="/task/run/dialog" hx-target="modal" hx-trigger="click" onclick="event.preventDefault()"'
                }
            ]

        # Default actions
        return []

    def populate(self, list: List[Task]):
        sep = ':'
        tasks = {t.name: t for t in list}
        path_names = sorted(tasks.keys())
        for name in path_names:
            # Build a hirarchical tree
            node = self
            task = tasks[name]
            keys = name.split(sep)
            while len(keys):
                key = keys[0]
                keys = keys[1:]
                node = node.child(key)  # Get or create the child node

                if not len(keys):
                    # Leaf element: This is the node where the task is located
                    node.update(task)

    def child(self, name):
        if not name in self.children:
            # Create an new child node
            subkey = name if not self.key else self.key + ':' + name

            self.children[name] = TaskNode(subkey, name)
        return self.children[name]

    def find(self, key):
        sep = ':'
        if sep in key:
            # Detected nested item key
            keys = key.split(sep)
            name = keys[0]
            if name in self.children:
                # Find sub key (if exists)
                subkey = sep.join(keys[1:])
                return self.children[name].find(subkey)
        elif key in self.children:
            # Key found as a child element
            return self.children[key]
        # Not found
        return None

    def update(self, value):
        self.value = value
