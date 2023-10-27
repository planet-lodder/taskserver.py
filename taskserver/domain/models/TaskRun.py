
import random
import string

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.Taskfile import Taskfile


def _new_id(size: int = 32):  # Pseudo random id, to track this edit session
    return ''.join(random.choice(string.ascii_letters) for i in range(size))


class TaskRun(BaseModel):
    id: str
    task: Task
    vars: TaskVars
    pid: Optional[int]
    started: Optional[datetime]
    finished: Optional[datetime]
    exitCode: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]

    def __init__(self, **kwargs): super().__init__(id=_new_id(), **kwargs)

    @property
    def ellapsed(self):
        if self.started and self.finished:
            return self.finished - self.started
        elif self.started:
            return datetime.now() - self.started
        else:
            return 0

    def start(self):
        self.started = datetime.now()
        try:
            path = self.task.path
            name = self.task.name
            vars = self.vars

            # TODO: This should be async
            print(f'Run task: {name} {vars}')
            output, err, res = Taskfile.run(path, name, vars)
            self.finished = datetime.now()

            self.stdout = output
            self.stderr = err
        except Exception as ex:
            # Record the time the task failed to finished
            self.finished = datetime.now()
            self.stderr = self.stderr or str(ex)
