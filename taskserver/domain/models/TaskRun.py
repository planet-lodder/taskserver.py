
import os
import random
import string
import subprocess

from typing import Optional, List
from datetime import datetime
from colorama import Fore, Style
from pydantic import BaseModel

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.Taskfile import Taskfile


def _new_id(size: int = 32):  # Pseudo random id, to track this edit session
    return ''.join(random.choice(string.ascii_letters) for i in range(size))


class TaskRun(BaseModel):
    id: str
    task: Task
    vars: TaskVars
    cli_args: Optional[str]
    pid: Optional[int]
    started: Optional[datetime]
    finished: Optional[datetime]
    exitCode: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]

    def __init__(self, **kwargs):
        kwargs["id"] = kwargs.get("id", _new_id())
        super().__init__(**kwargs)

    @property
    def ellapsed(self):
        if self.started and self.finished:
            return self.finished - self.started
        elif self.started:
            return datetime.now() - self.started
        else:
            return 0

    def start(self):
        self.started = datetime.now()
        try:
            path = self.task.path
            name = self.task.name
            vars = self.vars
            cli_args = self.cli_args

            # TODO: This should be async
            print(f'Run task: {name} {vars} -- {cli_args}')
            output, err, res = self.run(path, name, vars, cli_args)
            self.finished = datetime.now()

            self.stdout = output
            self.stderr = err
        except Exception as ex:
            # Record the time the task failed to finished
            print(f'{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}')
            self.finished = datetime.now()
            self.stderr = self.stderr or str(ex)

    def run(self, filename, action, vars={}, cli_args='') -> [str, str, subprocess.CompletedProcess]:
        try:
            command = f"task -t {filename} {action}"
            command = f'{command} -- {cli_args}' if cli_args else command

            clear = Style.RESET_ALL
            def green(msg): return f"{Fore.GREEN}{Style.BRIGHT}{msg}{clear}"
            def action(msg): return f"{Fore.MAGENTA}{msg}{clear}"
            print(f'{green("▶")} {action(command)}{Style.DIM}')

            # Set the ENV vars to pass to the process
            env = os.environ.copy()
            env.update(vars)

            # Build the command and run as sub process
            pop = command.split(" ")
            res = subprocess.run(
                pop,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            # Get the output and error streams
            out = res.stdout.decode().strip()
            err = res.stderr.decode().strip()

            # Return the execution details
            print(f'{Style.RESET_ALL}', end="")
            return out, err, res
        except Exception as e:
            print(f'{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}')
            print(f'{Style.RESET_ALL}', end="")
            return None, str(e), None
