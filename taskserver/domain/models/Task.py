
from typing import Dict, List, Optional
from pydantic import BaseModel


class TaskVars(dict[str, str]):
    raw = {}
    eval = {}

    class Config:
        exclude = ['raw', 'eval']


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
    src: str
    path: str
    name: str
    desc: str
    vars: Optional[Dict[str, str]]
    data: Optional[TaskBase]
    up_to_date: bool
