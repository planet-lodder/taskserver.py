
from typing import Optional, List
from pydantic import BaseModel

from taskserver.domain.models.Task import Task
from taskserver.domain.models.TaskSummary import TaskSummary


TASK_THREADS = {
    "Taskfile.yaml": {
        "start": [{"pid": 999}]
    }
}


class TaskState(BaseModel):
    has_child: bool
    running: bool
    up_to_date: bool


class TaskNode(BaseModel):
    path: str
    name: str

    # Optional state and metadata
    task: Optional[Task]  
    open: Optional[bool]

    # Add collection of child nodes
    summary: Optional[TaskSummary]
    children: Optional[dict]

    @property
    def state(self) -> TaskState:
        has_child = len(self.children.keys()) > 0 if self.children else False
        running = self.path in TASK_THREADS and self.name in TASK_THREADS[self.path]
        up_to_date = self.summary.up_to_date if self.summary else False
        return TaskState(
            has_child=has_child,
            running=running,
            up_to_date=up_to_date
        )

    @property
    def actions(self):
        task = self

        if self.name in TASK_THREADS["Taskfile.yaml"]:
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
                    "htmx": f'hx-target="main" hx-get="/task/details?name={self.name}"'
                },
                {
                    "name": "Run Task",
                    "icon": "icons/play.svg",
                    "htmx": f'hx-get="/task/run/dialog?name={self.name}" hx-target="modal" hx-trigger="click" onclick="event.preventDefault()"'
                }
            ]

        # Default actions
        return []

    def populate(self, data: List[TaskSummary], sep=':'):
        tasks = {t.name: t for t in data}
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
        if not self.children:
            self.children = {}
        if not name in self.children:
            # Create an new child node
            subkey = name if not self.name else self.name + ':' + name
            self.children[name] = TaskNode(
                path=self.path,
                name=subkey,
            )
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

    def update(self, info: TaskSummary):
        self.summary = info
        
