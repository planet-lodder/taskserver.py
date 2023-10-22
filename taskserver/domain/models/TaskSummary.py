
from taskserver.domain.models.Task import TaskBase


class TaskSummary(TaskBase):
    path: str
    name: str
    desc: str
    summary: str
    up_to_date: bool
