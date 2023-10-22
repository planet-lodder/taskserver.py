
from typing import Any, Optional
from taskserver.domain.models.Task import TaskBase


class TaskSummary(TaskBase):
    path: str
    name: str
    desc: str
    data: Optional[Any]
    summary: str
    up_to_date: bool