

from typing import List, Optional
from pydantic import BaseModel

from taskserver.domain.models.Task import TaskVars


class Command(BaseModel):
    type: str = 'cmd'
    value: str

    @property
    def text(self) -> str:
        return self.value


class TaskCommand(Command):
    type = 'task'
    open: Optional[bool]
    vars: Optional[TaskVars]
    cmds: Optional[List['Command']]
    up_to_date: Optional[bool]

    @property
    def text(self) -> str:
        return f"task {self.value}"

    def __init__(self, **kwargs):
        cmds = kwargs.get("cmds")
        if cmds:
            del kwargs["cmds"]
        super().__init__(**kwargs)
        if cmds:
            list = []
            for cmd in cmds:
                if cmd.get('type') == 'task':
                    list.append(TaskCommand(**cmd))
                else:
                    list.append(Command(**cmd))
            self.cmds = list
