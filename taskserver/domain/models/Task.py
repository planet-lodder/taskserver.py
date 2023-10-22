
import subprocess

from typing import List, Optional, Required
from pydantic import BaseModel


class TaskVars(dict[str, str]):
    pass


class TaskCmd(str):
    pass


class TaskBase(BaseModel):
    desc: Optional[str]
    vars: Optional[TaskVars]
    cmds: Optional[List[TaskCmd]]
    summary: Optional[str]
    sources: Optional[list]
    generates: Optional[list]
    required: Optional[list]


class Task(TaskBase):
    path: str
    name: str
    key: str
