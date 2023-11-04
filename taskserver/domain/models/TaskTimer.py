from typing import List
from taskserver.domain.models.TaskCommand import Command, TaskCommand
from taskserver.domain.models.TaskTracker import TaskTracker


class TaskTimer(TaskTracker):
    root: TaskCommand

    def __init__(self, root: TaskCommand) -> None:
        super().__init__()
        self.root = root

    def setOverflow(self, parent: Command, overflow: str): ...

    def cmdStarted(self, stack: List[TaskCommand], cmd_raw: str, up_to_date: bool = None):
        print(f'cmdStarted({cmd_raw}) [{up_to_date}]')
        # cmd = Command(raw=cmd_raw, up_to_date=up_to_date)
        # parent: TaskCommand = stack[-1] if len(stack) else None
        # parent.cmds.append(cmd)

    def taskStarted(self, stack: List[TaskCommand], cmd_name: str, up_to_date: bool = None):
        # Define a new task command node to track on the stack
        is_root = len(stack) == 0
        print(f'taskStarted({cmd_name}) [{up_to_date}]')
        if is_root:
            stack.append(self.root)  # Make root the active node
        elif parent := stack[-1] if len(stack) else None:
            cmd = next(filter(lambda c: c.raw == cmd_name, parent.cmds))
        if cmd:
            stack.append(cmd)  # Make this command the active node
        else:
            print(f'WARNING: Command "{cmd_name}" not found')

    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand):
        print(f'taskUpToDate({cmd.text})')
        cmd.up_to_date = True

    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand):
        print(f'taskFinished({cmd.text})')

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand):
        print(f'taskFailed({cmd.text})')

