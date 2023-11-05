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
            self.markFinishedUpTo(parent, cmd)
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
            # self.markFinishedUpTo(stack[-1] if not is_root else self.root, cmd)
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
        parent = stack[-1] if len(stack) else None
        self.markFinishedUpTo(parent, cmd)
        self.closeTask(cmd)

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand, exitCode=1):
        # If this is a task command, check last child prcess that was finished
        def mark_last_run_as_failed(parent: Command):
            parent.exitCode = exitCode
            if isinstance(parent, TaskCommand) and parent.cmds:
                # Find all previous siblings that needs to be closed
                found = list(filter(lambda c: c.finished, parent.cmds))
                if last := found[-1] if len(found) else None:
                    mark_last_run_as_failed(last)

        # Set current task exit code
        mark_last_run_as_failed(cmd)

        # Add exitCode all the way up to root
        for parent in stack:
            parent.exitCode = exitCode
        self.closeTask(cmd)

    def markFinishedUpTo(self, parent: TaskCommand, cmd: Command):
        if not parent and cmd:
            # Mark the current command as finished
            cmd.finished = datetime.now()
        elif parent and isinstance(parent, TaskCommand):
            # Find all previous siblings that needs to be closed
            found = filter(lambda c: not c.finished, parent.cmds)
            while sibling := next(found):
                sibling.finished = datetime.now()
                if sibling == cmd:
                    return  # Break here, do not mar future tasks as complete

    def closeTask(self, cmd: TaskCommand):
        cmd.finished = cmd.finished or datetime.now()
        self.save()
