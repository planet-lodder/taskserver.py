
from taskserver.models.Task import Task


class TaskFactory():
    key = "test"
    name = "test"
    sources = ["requirements.txt"]
    generates = ["dist/**"]

    class Meta:
        model = Task
