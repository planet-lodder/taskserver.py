
import json
import random
import string

from typing import Optional
from datetime import datetime
from colorama import Fore, Style
from pydantic import BaseModel

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.TaskBreakdown import TaskBreakdown
from taskserver.domain.models.Taskfile import Taskfile


def bold(msg): return f"{Style.BRIGHT}{msg}{Style.NORMAL}"
def red(msg): return f"{Fore.RED}{bold(msg)}{Style.RESET_ALL}"
def green(msg): return f"{Fore.GREEN}{msg}{Style.RESET_ALL}"
def action(msg): return f"{Fore.MAGENTA}{msg}{Style.RESET_ALL}"
def debug(msg): return f"{Style.DIM}{msg}{Style.RESET_ALL}"


def _new_id(size: int = 32):  # Pseudo random id, to track this edit session
    return ''.join(random.choice(string.ascii_letters) for i in range(size))


class TaskRun(BaseModel):
    id: str
    task: Task
    vars: TaskVars
    cli_args: Optional[str]
    breakdown: Optional[TaskBreakdown]
    pid: Optional[int]
    started: Optional[datetime]
    finished: Optional[datetime]
    stopped: Optional[bool]
    exitCode: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]

    class Config:
        exclude = []

    def __init__(self, **kwargs):
        kwargs["id"] = kwargs.get("id") or _new_id()
        super().__init__(**kwargs)

    @property
    def ellapsed(self):
        if self.started and self.finished:
            return self.finished - self.started
        elif self.started:
            return datetime.now() - self.started
        else:
            return 0

    @property
    def arguments(self):
        args = []

        if self.task.path != "Taskfile.yaml":
            args = ['-t', self.task.path]  # Specify custom taskfile

        # Add overrides for task vars
        for var in self.vars:
            if self.vars[var] != self.vars.eval[var]:
                args += [f'{var}={json.dumps(self.vars[var])}']

        # Add the task by name
        args += [self.task.name]

        # Add extra CLI args for sub process
        if extra := self.cli_args:
            args.append(['--'] + extra if type(extra) == list else [])

        # Return combined arguments
        return args

    @property
    def command(self):
        command = ''
        args = ['task'] + self.arguments
        sep = ''
        for arg in args:
            arg = json.dumps(arg) if " " in arg and not '"' in arg else arg
            command += sep + arg
            sep = ' '
        return command

    def timed(self) -> str:
        timed = self.ellapsed
        return timed

    def trace(self, command: str):
        extra = debug(f'# --> {self.id}')
        print(f'{green("▶")} {action(command)} {extra}{Style.RESET_ALL}')

    def traceDone(self, command: str):
        glyph = green("◀")
        command = green(command)
        extra = debug(f'# <-- {self.id} ( {self.timed()} )')
        print(f'{glyph} {command} {extra}{Style.RESET_ALL}')

    def traceError(self, command: str):
        glyph = red("■")
        command = red(command + f" [ {self.exitCode} ]")
        extra = debug(f'# <-- {self.id} ( {self.timed()} )')
        print(f'{glyph} {command} {extra}{Style.RESET_ALL}')
