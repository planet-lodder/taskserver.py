

import json
import os
import subprocess
from typing import List
from pydantic import BaseModel
import yaml

from taskserver.domain.models.Task import Task, TaskVars


class TaskfileIncludes(dict[str, str]):
    pass


class TaskfileEnvs(TaskVars):
    pass


class TaskfileVars(TaskVars):
    pass


class Taskfile(BaseModel):
    version: str
    env: TaskfileEnvs
    vars: TaskfileVars
    includes: TaskfileIncludes
    #tasks: List[Task]

    @staticmethod
    def load(path):
        if not os.path.isfile(path):
            raise Exception(f"Taskfile {path} not found!")

        # Load the raw config file for this taskfile
        with open(path, "r") as stream:
            raw = yaml.safe_load(stream)
            res = Taskfile(**raw)
            return res

    @staticmethod
    def run(filename, command, extra_args='') -> [str, str, subprocess.CompletedProcess]:
        try:
            pop = f"task -t {filename} {command} -- {extra_args}".split(" ")
            res = subprocess.run(
                pop,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out = res.stdout.decode().strip()
            err = res.stderr.decode().strip()
            return out, err, res
        except Exception as e:
            return None, str(e), None

    @staticmethod
    def listAll(filename) -> List[Task]:
        try:
            # Run: task --list-all --json
            output, err, res = Taskfile.run(filename, '--list-all --json')
            # Parse the JSON into a list of tasks
            obj = json.loads(output)

            # Parse the items into a list
            list = obj.get("tasks", [])
            path = obj.get("location", "")
            base = os.path.dirname(path) if path else os.getcwd()
            tasks = []
            for item in list:
                # Update and normalize paths for all tasks by stripping base folder prefix
                loc = item.get("location", {})
                path = loc.get("taskfile", '')
                path = path.removeprefix(base + "/")
                task = Task(
                    file=path,
                    key=item.get("name"),
                    name=item.get("name"),
                    desc=item.get("desc"),
                    summary=item.get('summary', ''),
                    vars=item.get('vars', {}),
                    sources=item.get('sources', []),
                    generates=item.get('generates', {}),
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {filename}.')
