
import json
import os
import random
import string
import subprocess
import threading
import time
import asyncio

from typing import Any, Callable, Coroutine, Optional, List
from datetime import datetime
from colorama import Fore, Style
from pydantic import BaseModel

from taskserver.domain.models.Task import Task, TaskVars
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
    pid: Optional[int]
    started: Optional[datetime]
    finished: Optional[datetime]
    exitCode: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]

    # proc: Optional[subprocess.Popen]

    class Config:
        exclude = ['proc']

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

    @property
    def arguments(self):
        args = [self.task.name]
        if self.task.path != "Taskfile.yaml":
            # Custome taskfile provided
            args = ['-t', self.task.path, self.task.name]
        if extra := self.cli_args:
            # Add extra CLI args for sub process
            args.append(['--'] + extra if type(extra) == list else [])
        # Return combined arguments
        return args

    @property
    def command(self):
        command = ''
        sep = ''
        args = ['task'] + self.arguments
        for arg in args:
            arg = arg if not " " in arg else json.dumps(arg)
            command += sep + arg
            sep = ' '
        return command

    def start(self):
        self.started = datetime.now()
        try:
            # Set the ENV vars to pass to the process
            env = os.environ.copy()
            env.update(self.vars)

            self.stdout = f'{self.id}/stdout.log'
            self.stderr = f'{self.id}/stderr.log'

            # Print the executed command to stdout
            self.trace(self.command)

            # Start the process (non-blocking)
            proc = subprocess.Popen(
                ['task'] + self.arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            self.pid = proc.pid

            # Run the (deferred, async) action in a new thread, to make it non-blocking
            def deferred():
                result = asyncio.run(self.trackChanges(proc))
                self.runCompleted(result, proc)

            # Spawn task in new tread, but do not wait...
            threading.Thread(target=deferred).start()

        except Exception as ex:
            self.finished = datetime.now()
            # Record the time the task failed to finished
            print(f'{Fore.RED}ERROR: {str(ex)}{Style.RESET_ALL}')

    async def trackChanges(self, proc: subprocess.Popen):
        # Wait for a return code
        while proc.poll() == None:
            time.sleep(.5)
        return proc.returncode

    def runCompleted(self, result: int, proc: subprocess.Popen):
        # Stop timer and set the exit code that was returned
        self.finished = datetime.now()
        self.exitCode = result

        # Check the exit condition (success/fail)
        if result == 0:
            # Run completed successfully
            self.traceDone(self.command)
        elif result > 0:
            # Run failed with an exit code
            self.traceError(self.command)

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
