
import subprocess

from typing import Any, Dict, List, Optional, Required
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


class Task(BaseModel):
    path: str
    name: str
    desc: str
    vars: Optional[Dict[str, str]]
    data: Optional[TaskBase]
    up_to_date: bool
