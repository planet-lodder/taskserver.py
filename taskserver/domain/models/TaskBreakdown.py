import re

from typing import List, Optional
from colorama import Fore, Style

from taskserver.domain.models.TaskCommand import Command, TaskCommand
from taskserver.domain.models.TaskTimer import TaskTimer
from taskserver.domain.models.TaskTracker import TaskTracker

from taskserver.domain.models.Taskfile import Taskfile

class TaskParser(TaskTracker):
    root: TaskCommand
    stack: List[TaskCommand]

    def __init__(self, root: TaskCommand) -> None:
        super().__init__()
        self.root = root
        self.stack = []

    def setOverflow(self, parent: Command, overflow: str):
        if parent and len(parent.cmds):
            parent.cmds[-1].value = parent.cmds[-1].value + overflow

    def cmdStarted(self, stack: List[TaskCommand], cmd_raw: str, up_to_date: bool = None):
        cmd = Command(value=cmd_raw, up_to_date=up_to_date)
        parent: TaskCommand = stack[-1] if len(stack) else None
        parent.cmds.append(cmd)

    def taskStarted(self, stack: List[TaskCommand], cmd_name: str, up_to_date: bool = None):
        # Define a new task command node to track on the stack
        is_root = len(stack) == 0
        cmd = self.root if is_root else TaskCommand(
            value=cmd_name,
            up_to_date=up_to_date
        )
        if parent := stack[-1] if len(stack) else None:
            parent.cmds.append(cmd)  # Append to the parent node
        stack.append(cmd)  # Make this the active node

    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand):
        # Forcefully get the sub task breakdown
        cmd.up_to_date = True
        TaskBreakdown.forTask(
            self.root.path,
            cmd.value,
            True,
            up_to_date=True,
            existing_root=cmd,
        )

    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand): ...


class TaskBreakdown(TaskCommand):
    path: str

    class Config:
        exclude = ['stack', 'debug']

    @staticmethod
    def forTask(filename,
                task_name: str,
                force: bool = False,
                up_to_date: bool = None,
                existing_root: TaskCommand = None):
        # Do a dry run and capture the traced commands (to rebuild a execution tree)
        command = f"{task_name} --dry --verbose"
        command = command + ' -f' if force else command
        _, stderr, res = Taskfile.run(filename, command)
        if res.returncode > 0:
            message = f'Task "{task_name}" failed to run in dry run mode.'
            raise Exception(message)

        # Define the root node
        root = TaskBreakdown(
            path=filename,
            value=task_name,
            up_to_date=up_to_date,
            cmds=[]
        )
        parser = TaskParser(root)

        # Read the trace logs to reconstruct the task breakdown
        if buffer := stderr:
            root.feed(
                buffer,
                up_to_date=up_to_date,
                existing_root=existing_root,
                actions=parser,
            )

        return root

    def feed(self,
             buffer: str,
             actions: TaskTracker,
             up_to_date: bool = None,
             existing_root: TaskCommand = None,
             ):
        stack = actions.stack
        task_name = self.value
        silent = existing_root != None
        actions = actions or TaskTimer(self)
        debug = False

        def trace(message, prefix='', extra=''):
            if not debug:
                return
            prefix = f'{Style.DIM}{prefix}{Style.RESET_ALL}' if prefix else ''
            prefix = ('   '*len(stack)) + prefix
            message = f'{Style.BRIGHT}{message}{Style.RESET_ALL}'
            extra = f'{Style.DIM}({extra}){Style.RESET_ALL}' if extra else ''
            print(f'{prefix}{message} {extra}')

        def warn(message):
            prefix = f'{Style.BRIGHT}WARNING:{Style.NORMAL} '
            print(f'{Fore.YELLOW}{prefix}{message}{Style.RESET_ALL}')

        while match := re.search(r'((task: )(.*))+', buffer, re.MULTILINE):

            # Fetch the relevant parts from the regex match
            groups = match.groups()
            overflow = buffer[:match.start()].rstrip()
            line = groups[2] if len(groups) >= 3 else ''
            buffer = buffer[match.end():]  # to find next match
            parent: TaskCommand = stack[-1] if len(stack) else None
            if parent and not parent.cmds:
                parent.cmds = []

            # Append overflow from prev. command (this happens for multiline cmds)
            if overflow and actions:
                actions.setOverflow(parent, overflow)

            if check := re.search(r'\"(.*)\" started', line):
                # Task start tag detected
                cmd_name = check.groups()[0]
                if existing_root and existing_root.value == cmd_name:
                    stack.append(existing_root)  # silently add
                elif not parent and cmd_name == task_name:
                    # Root task is starting...
                    trace(cmd_name, f' -> Task: ', 'root')
                    actions.taskStarted(stack, cmd_name, up_to_date)
                else:
                    # New sub task has started, add to parent
                    trace(cmd_name, f' -> Task: ', 'started')
                    actions.taskStarted(stack, cmd_name, up_to_date)

            elif check := re.search(r'\"(.*)\" finished', line):
                # Task close tag has been detected
                last = stack.pop()
                cmd_name = check.groups()[0]

                if not silent and self.value != cmd_name:
                    trace(cmd_name, f' <- Task: ', 'finished')

                # Track the task finishing
                actions.taskFinished(stack, last)

                if cmd_name == task_name and not len(stack) and (last != self or len(stack)):
                    # Main task has finished
                    warn(f'Commands are left on the stack after main task exits.')
                elif last.value != cmd_name:
                    # Sub task finished
                    warn(f'Expected "task {cmd_name}", got "{last.text}".')

            elif check := re.search(r'Task \"(.*)\" is up to date', line):
                # Task is up to date
                last = stack.pop()
                last.up_to_date = True
                cmd_name = check.groups()[0]
                if last.value != cmd_name:
                    warn(f'Expected "task {cmd_name}", got "{last.text}".')

                # Trigger action when task is up to date
                actions.taskUpToDate(stack, last)
                trace(cmd_name, f' <- Task: ', 'up to date')

            elif check := re.search(r'\[(.*)\] (.*)', line):
                # This is a command being executed
                cmd_name = check.groups()[0]
                cmd_raw = check.groups()[1]

                if parent and parent.value == cmd_name:
                    trace('', f' -> Cmd: ' + cmd_raw)
                    actions.cmdStarted(stack, cmd_raw, up_to_date=up_to_date)
                else:
                    warn(f'Found an orphan command: {cmd_raw} ({cmd_name})')
            elif check := re.search(r'(Failed to run task \"(.*)\": )+(exit status (\d+))', line):
                groups = check.groups()
                last = stack.pop() if len(stack) else self
                code = groups[-1]
                actions.taskFailed(stack, last, int(code))
            else:
                warn(f'Line not recognised: "{line}"')

        # Edge case: Check for overflow on last command
        parent = stack[-1] if len(stack) else None
        if parent and buffer and actions:
            actions.setOverflow(parent, buffer)

