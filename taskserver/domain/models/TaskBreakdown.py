from abc import ABC, abstractmethod
import re
from typing import Callable, List, Optional
from colorama import Fore, Style

from pydantic import BaseModel
from taskserver.domain.models.Task import TaskVars

from taskserver.domain.models.Taskfile import Taskfile


class Command(BaseModel):
    type: str = 'cmd'
    raw: str
    open: Optional[bool]
    vars: Optional[TaskVars]
    cmds: Optional[List['Command']]
    up_to_date: Optional[bool]

    @property
    def text(self) -> str:
        return self.raw

    def __init__(self, **kwargs):
        cmds = kwargs.get("cmds")
        if cmds:
            del kwargs["cmds"]
        super().__init__(**kwargs)
        if cmds:
            list = []
            for cmd in cmds:
                if cmd.get('type') == 'task':
                    list.append(TaskCommand(**cmd))
                else:
                    list.append(Command(**cmd))
            self.cmds = list


class TaskCommand(Command):
    type = 'task'

    @property
    def text(self) -> str:
        return f"task {self.raw}"


class TaskTracker(ABC):
    @abstractmethod
    def setOverflow(self, parent: Command, overflow: str): ...

    @abstractmethod
    def cmdStarted(self, stack: List[TaskCommand],
                   cmd_raw: str, up_to_date: bool = None): ...

    @abstractmethod
    def taskStarted(self, stack: List[TaskCommand],
                    cmd_name: str, up_to_date: bool = None): ...

    @abstractmethod
    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    @abstractmethod
    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    @abstractmethod
    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand): ...


class TaskParser(TaskTracker):
    root: TaskCommand

    def __init__(self, root: TaskCommand) -> None:
        super().__init__()
        self.root = root

    def setOverflow(self, parent: Command, overflow: str):
        if parent and len(parent.cmds):
            parent.cmds[-1].raw = parent.cmds[-1].raw + overflow

    def cmdStarted(self, stack: List[TaskCommand], cmd_raw: str, up_to_date: bool = None):
        cmd = Command(raw=cmd_raw, up_to_date=up_to_date)
        parent: TaskCommand = stack[-1] if len(stack) else None
        parent.cmds.append(cmd)

    def taskStarted(self, stack: List[TaskCommand], cmd_name: str, up_to_date: bool = None):
        # Define a new task command node to track on the stack
        is_root = len(stack) == 0
        cmd = self.root if is_root else TaskCommand(
            raw=cmd_name,
            up_to_date=up_to_date
        )
        if parent := stack[-1] if len(stack) else None:
            parent.cmds.append(cmd)  # Append to the parent node
        stack.append(cmd)  # Make this the active node

    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand):
        # Forcefully get the sub task breakdown
        TaskBreakdown.forTask(
            self.root.path,
            cmd.raw,
            True,
            up_to_date=True,
            existing_root=cmd,
        )
        cmd.up_to_date = True

    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand): ...


class TaskParser(TaskTracker):
    root: TaskCommand

    def __init__(self, root: TaskCommand) -> None:
        super().__init__()
        self.root = root

    def setOverflow(self, parent: Command, overflow: str):
        if parent and len(parent.cmds):
            parent.cmds[-1].raw = parent.cmds[-1].raw + overflow

    def cmdStarted(self, stack: List[TaskCommand], cmd_raw: str, up_to_date: bool = None):
        cmd = Command(raw=cmd_raw, up_to_date=up_to_date)
        parent: TaskCommand = stack[-1] if len(stack) else None
        parent.cmds.append(cmd)

    def taskStarted(self, stack: List[TaskCommand], cmd_name: str, up_to_date: bool = None):
        # Define a new task command node to track on the stack
        is_root = len(stack) == 0
        cmd = self.root if is_root else TaskCommand(
            raw=cmd_name,
            up_to_date=up_to_date
        )
        if parent := stack[-1] if len(stack) else None:
            parent.cmds.append(cmd)  # Append to the parent node
        stack.append(cmd)  # Make this the active node

    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand):
        # Forcefully get the sub task breakdown
        TaskBreakdown.forTask(
            self.root.path,
            cmd.raw,
            True,
            up_to_date=True,
            existing_root=cmd,
        )
        cmd.up_to_date = True

    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand): ...

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand): ...


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


class TaskBreakdown(TaskCommand):
    path: str
    name: str
    stack: List[TaskCommand] = []
    debug = True

    class Config:
        exclude = ['stack', 'debug']

    def feed(self,
             buffer: str,
             actions: TaskTracker = None,
             dry_run: bool = False,
             up_to_date: bool = None,
             silent: bool = False,
             ):
        stack = self.stack
        task_name = self.raw
        actions = actions or TaskTimer(self)

        def trace(message, prefix='', extra=''):
            if not self.debug:
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
                if silent and self.raw == cmd_name:
                    ...  # silently add
                elif not parent and cmd_name == task_name:
                    # Root task is starting...
                    trace(cmd_name, f' -> Task: ', 'root')
                else:
                    # New sub task has started, add to parent
                    trace(cmd_name, f' -> Task: ', 'started')

                # Define or track task starting
                actions.taskStarted(stack, cmd_name, up_to_date)

            elif check := re.search(r'\"(.*)\" finished', line):
                # Task close tag has been detected
                last = stack.pop()
                cmd_name = check.groups()[0]

                if not silent and self.raw != cmd_name:
                    trace(cmd_name, f' <- Task: ', 'finished')

                # Track the task finishing
                actions.taskFinished(stack, last)

                if cmd_name == task_name and not len(stack) and (last != self or len(stack)):
                    # Main task has finished
                    warn(f'Commands are left on the stack after main task exits.')
                elif last.raw != cmd_name:
                    # Sub task finished
                    warn(f'Expected "task {cmd_name}", got "{last.text}".')

            elif check := re.search(r'Task \"(.*)\" is up to date', line):
                # Task is up to date
                last = stack.pop()
                last.up_to_date = True
                cmd_name = check.groups()[0]
                if last.raw != cmd_name:
                    warn(f'Expected "task {cmd_name}", got "{last.text}".')

                # Trigger action when task is up to date
                actions.taskUpToDate(stack, last)
                trace(cmd_name, f' <- Task: ', 'up to date')

            elif check := re.search(r'\[(.*)\] (.*)', line):
                # This is a command being executed
                cmd_name = check.groups()[0]
                cmd_raw = check.groups()[1]
                if parent.raw == cmd_name:
                    trace('', f' -> Cmd: ' + cmd_raw)
                    actions.cmdStarted(stack, cmd_raw, up_to_date=up_to_date)
                else:
                    warn(f'Found an orphan command: {cmd_raw} ({cmd_name})')
            else:
                warn(f'Line not recognised: {line}')

        # Edge case: Check for overflow on last command
        if parent and buffer and actions:
            actions.setOverflow(parent, buffer)

        return buffer

    @staticmethod
    def forTask(filename, task_name, force=False, up_to_date=False, existing_root=None):
        # Do a dry run and capture the traced commands (to rebuild a execution tree)
        command = f"{task_name} --dry --verbose"
        command = command + ' -f' if force else command
        _, stderr, res = Taskfile.run(filename, command)
        if res.returncode > 0:
            message = f'Task "{task_name}" failed to run in dry run mode.'
            raise Exception(message)

        # Define the root node
        root = existing_root or TaskBreakdown(
            path=filename,
            name=task_name,
            raw=task_name,
            up_to_date=up_to_date
        )

        # Read the trace logs to reconstruct the task breakdown
        if buffer := stderr:
            root.feed(
                buffer,
                dry_run=True,
                up_to_date=up_to_date,
                silent=existing_root != None,
                actions=TaskParser(root),
            )

        return root
