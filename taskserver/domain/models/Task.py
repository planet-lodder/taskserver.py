
from typing import List, Optional, Required
from pydantic import BaseModel


class TaskVars(dict[str, str]):
    pass


class Task(BaseModel):
    file: str
    key: str
    name: str
    desc: Optional[str]
    vars: Optional[TaskVars]
    summary: Optional[str]
    sources: Optional[list]
    generates: Optional[list]
    required: Optional[list]
