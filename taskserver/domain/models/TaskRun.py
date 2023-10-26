
import random
import string
from typing import Optional, List
from pydantic import BaseModel

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.Taskfile import Taskfile


def _new_id(size: int):  # Pseudo random id, to track this edit session
    return ''.join(random.choice(string.ascii_letters) for i in range(size))


class TaskRun(BaseModel):
    key: str
    task: Task
    vars: TaskVars
    pid: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    exitCode: Optional[int]

    def __init__(self, **kwargs):
        super().__init__(key=_new_id(32), **kwargs)

    def start(self):
        path = self.task.path
        name = self.task.name
        vars = self.vars

        print(f'Run task: {name} {vars}')
        output, err, res = Taskfile.run(path, name, vars)

        self.stdout = output
        self.stderr = err
