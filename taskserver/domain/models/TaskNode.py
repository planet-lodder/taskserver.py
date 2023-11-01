
from typing import Optional, List
from pydantic import BaseModel

from taskserver.domain.models.Task import Task


class TaskState(BaseModel):
    has_child: bool
    running: bool
    up_to_date: bool


class TaskNode(BaseModel):
    path: str
    name: str
    data: Optional[Task]
    children: Optional[dict]

    # Optional state and child nodes
    open: Optional[bool]
    runs: Optional[dict]

    class Config:
        exclude = ['runs', 'is_running', 'has_children', 'up_to_date']

    @property
    def is_running(self) -> bool:
        return True if self.runs and len(self.runs.keys()) else False

    @property
    def up_to_date(self) -> bool:
        return self.data.up_to_date if self.data else False

    def populate(self, data: List[Task], sep=':'):
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
                    node.data = task

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
