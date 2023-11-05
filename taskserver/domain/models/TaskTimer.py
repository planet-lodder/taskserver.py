from datetime import datetime
from typing import Callable, List
from taskserver.domain.models.TaskCommand import Command, TaskCommand
from taskserver.domain.models.TaskTracker import TaskTracker


class TaskTimer(TaskTracker):
    root: TaskCommand
    onUpdate: Callable

    def __init__(self, root: TaskCommand, onUpdate=None) -> None:
        super().__init__()
        self.root = root
        self.onUpdate = onUpdate

    def save(self):
        if self.onUpdate:
            self.onUpdate()

    def setOverflow(self, parent: Command, overflow: str): ...

    def cmdStarted(self, stack: List[TaskCommand], cmd_raw: str, up_to_date: bool = None):
        parent: TaskCommand = stack[-1] if len(stack) else None
        cmds = parent.cmds if parent else []
        if cmd := next(filter(lambda c: c.value.startswith(cmd_raw), cmds)):
            cmd.started = datetime.now()
            self.save()

    def taskStarted(self, stack: List[TaskCommand], cmd_name: str, up_to_date: bool = None):
        # Define a new task command node to track on the stack
        is_root = len(stack) == 0
        if is_root:
            # Make root the active node
            cmd = self.root
        elif parent := stack[-1] if len(stack) else None:
            # Find a matching node in the commands
            cmd = next(filter(lambda c: c.value == cmd_name, parent.cmds))
        if cmd:
            cmd.started = datetime.now()
            stack.append(cmd)  # Make this command the active node
            self.save()
        else:
            print(f'WARNING: Command "{cmd_name}" not found')

    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand):
        if cmd:
            cmd.up_to_date = True
            cmd.started = datetime.now()
            cmd.finished = cmd.started
            self.closeTask(cmd)

    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand):
        self.closeTask(cmd)

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand, exitCode = 1):
        cmd.exitCode = exitCode
        self.closeTask(cmd)

    def closeTask(self, cmd: TaskCommand):
        cmd.finished = cmd.finished or datetime.now()
        if isinstance(cmd, TaskCommand):
            for item in cmd.cmds:
                self.closeTask(item)
        self.save()
