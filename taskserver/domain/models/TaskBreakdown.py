import re
from typing import List, Optional
from colorama import Fore, Style

from pydantic import BaseModel
from taskserver.domain.models.Task import TaskVars

from taskserver.domain.models.Taskfile import Taskfile


class Command(BaseModel):
    type: str = 'cmd'
    raw: str

    @property
    def text(self) -> str:
        return self.raw


class TaskCommand(Command):
    type = 'task'
    open: Optional[bool]
    vars: Optional[TaskVars]
    cmds: Optional[List[Command]]
    up_to_date: Optional[bool]

    @property
    def text(self) -> str:
        return f"task {self.raw}"


class TaskBreakdown(TaskCommand):

    @staticmethod
    def forTask(filename, task_name):
        # Do a dry run and capture the traced commands (to rebuild a execution tree)
        command = f"{task_name} --dry --verbose -f"
        output, stderr, res = Taskfile.run(filename, command)
        if res.returncode > 0:
            message = f'Task "{task_name}" failed to run in dry run mode.'
            raise Exception(message)

        # Read the trace logs to reconstruct the task breakdown
        root = TaskBreakdown(raw=task_name)
        stack: List[TaskCommand] = []

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

        buffer = stderr
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
            if overflow and parent and len(parent.cmds):
                parent.cmds[-1].raw = parent.cmds[-1].raw + overflow

            if check := re.search(r'\"(.*)\" started', line):
                # Task start tag detected
                cmd_name = check.groups()[0]
                trace(cmd_name, f' -> Task: ', 'started')
                if not parent and cmd_name == task_name:
                    # Root task is starting...
                    stack.append(root)
                else:
                    # New sub task has started, add to parent
                    cmd = TaskCommand(raw=cmd_name)
                    if parent:
                        parent.cmds.append(cmd)
                    stack.append(cmd)
            elif check := re.search(r'\"(.*)\" finished', line):
                # Task close tag has been detected
                last = stack.pop()
                cmd_name = check.groups()[0]
                trace(cmd_name, f' <- Task: ', 'finished')
                if cmd_name == task_name and not len(stack) and (last != root or len(stack)):
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
                trace(cmd_name, f' <- Task: ', 'up to date')
                if last.raw != cmd_name:
                    warn(f'Expected "task {cmd_name}", got "{last.text}".')
            elif check := re.search(r'\[(.*)\] (.*)', line):
                # This is a command being executed
                cmd_name = check.groups()[0]
                cmd_raw = check.groups()[1]
                if parent.raw == cmd_name:
                    trace('', f' -> Cmd: ' + cmd_raw)
                    cmd = Command(raw=cmd_raw)
                    parent.cmds.append(cmd)
                else:
                    warn(f'Found an orphan command: {cmd_raw} ({cmd_name})')
            else:
                warn(f'Line not recognised: {line}')

        # Edge case: Check for overflow on last command
        if buffer:
            parent.cmds[-1].raw = parent.cmds[-1].raw + buffer

        return root.cmds
