

import json
import os
import re
import subprocess
from typing import Any, List, Dict
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
    path: str
    version: str
    env: TaskfileEnvs
    vars: TaskfileVars
    includes: TaskfileIncludes
    tasks: Dict[str, Any]

    class Config:
        exclude = ['path']

    @staticmethod
    def tryLoad(path):
        try:
            # Try and load existing taskfile
            return Taskfile.load(path)
        except:
            return Taskfile(path=path, includes={}, version=3, env={}, vars={}, tasks={})

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
    def run(filename, command, vars={}, extra_args='') -> [str, str, subprocess.CompletedProcess]:
        try:

            # Set the ENV vars to pass to the process
            env = os.environ.copy()
            env.update(vars)

            # Build the command and run as sub process
            pop = f"task -t {filename} {command} -- {extra_args}".split(" ")
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
            return out, err, res
        except Exception as e:
            return None, str(e), None

    @staticmethod
    def summary(filename, task_name):
        output, _, _ = Taskfile.run(filename, f"{task_name} --summary")
        return output

    @staticmethod
    def breakdown(filename, task_name):
        output = Taskfile.summary(filename, task_name)

        # Strip everything up to the commands
        output = re.sub(r'(?is).*commands:', '', output, flags=re.MULTILINE)
        commands = []
        type = 'cmd'
        while output:
            match = re.search(r'( - )(Task: )?', output, re.MULTILINE)

            if not match and output:
                # Assume this is a single command
                commands.append({
                    "type": type,
                    "message": output,
                })
                output = ''
            else:
                # Detected the start of a new command
                groups = match.groups()
                start = match.start()
                end = match.end()

                # If there is commands in the buffer, add as the (prev) command
                buffer = output[:start].strip()
                if buffer:
                    commands.append({
                        "type": type,
                        "message": buffer,
                    })

                # Check if this has a task prefix
                type = 'cmd'
                if len(groups) > 1 and 'Task: ' in groups:
                    type = 'task'

                # Find next item entry
                output = output[end:]

        return commands

    @staticmethod
    def listTasks(filename: str) -> List[Task]:
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
                    path=path,
                    name=item.get("name"),
                    desc=item.get("desc"),
                    up_to_date=bool(item.get('up_to_date', False)),
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {filename}.')
