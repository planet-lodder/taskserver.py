

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from taskserver.domain.models.Task import TaskVars


class Command(BaseModel):
    type: str = 'cmd'
    value: str
    started: Optional[datetime]
    finished: Optional[datetime]
    stopped: Optional[bool]
    exitCode: Optional[int]
    up_to_date: Optional[bool]

    @property
    def text(self) -> str:
        return self.value

    @property
    def has_error(self) -> bool:
        return self.exitCode and self.exitCode > 0
    
    @property
    def is_busy(self) -> bool:
        return self.started and not self.finished

    @property
    def ellapsed(self):
        if self.started and self.finished:
            return self.finished - self.started
        elif self.started:
            return datetime.now() - self.started
        else:
            return 0


class TaskCommand(Command):
    type = 'task'
    open: Optional[bool]
    vars: Optional[TaskVars]
    cmds: Optional[List['Command']]    

    @property
    def text(self) -> str:
        return f"task {self.value}"

    @property
    def is_busy(self) -> bool:
        if self.started and not self.finished:
            return True
        for cmd in self.cmds or []:
            if cmd.is_busy:
                return True
        return False

    @property
    def has_error(self) -> bool:
        if self.exitCode or not self.cmds:
            return self.exitCode and self.exitCode > 0
        for cmd in self.cmds:
            if cmd.has_error:
                return True
        return False

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
