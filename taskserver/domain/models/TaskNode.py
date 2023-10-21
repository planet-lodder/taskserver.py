
from ast import List
from typing import Optional
from pydantic import BaseModel

from taskserver.domain.models.Task import Task


class TaskNode(BaseModel):
    file: str           # TODO: Renamed from 'path'
    key: str
    name: str

    # Optional state and metadata
    task: Optional[Task]  # TODO: Renamed from 'value'
    info: Optional[dict]  # TODO: Renamed from 'state'
    open: Optional[bool]

    # Add collection of child nodes
    children: Optional[dict]

    def populate(self, data: List[Task], sep = ':'):        
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

    def update(self, data: Task):
        self.task = data
