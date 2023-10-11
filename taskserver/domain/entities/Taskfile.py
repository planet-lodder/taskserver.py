

from typing import List
from pydantic import BaseModel

from taskserver.domain.entities.Task import Task, TaskVars



class TaskfileIncludes(dict[str, str]):
    pass


class TaskfileEnvs(TaskVars):
    pass


class TaskfileVars(TaskVars):
    pass


class Taskfile(BaseModel):
    version: str
    includes: TaskfileIncludes
    env: TaskfileEnvs
    vars: TaskfileVars
    tasks: List[Task]
