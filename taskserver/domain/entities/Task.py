
from pydantic import BaseModel


class TaskVars(dict[str, str]):
    pass


class Task(BaseModel):
    key: str
    name: str
    desc: str
    vars: TaskVars
    sources: list(str)
    generates: list(str)
