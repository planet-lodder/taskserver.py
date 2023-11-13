

import json
import os
import re
import subprocess
from typing import Any, List, Dict
from colorama import Fore, Style
from pydantic import BaseModel
import yaml

from taskserver.domain.models.Task import Task, TaskVars


class TaskfileIncludes(Dict[str, str]):
    pass


class TaskfileEnvs(TaskVars):
    pass


class TaskfileVars(TaskVars):
    pass


class Taskfile(BaseModel):
    path: str
    version: str
    env: TaskfileEnvs
    vars: TaskfileVars
    includes: TaskfileIncludes
    tasks: Dict[str, Any]

    class Config:
        exclude = ['path']

    @staticmethod
    def load(path):
        if not os.path.isfile(path):
            raise Exception(f"Taskfile {path} not found!")

        # Load the raw config file for this taskfile
        with open(path, "r") as stream:
            raw = yaml.safe_load(stream)
            res = Taskfile(path=path, **raw)
            return res

    @staticmethod
    def run(filename, action, vars={}, cli_args='') -> [str, str, subprocess.CompletedProcess]:
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
            print(f'{Style.RESET_ALL}', end="")
            return None, str(e), None
