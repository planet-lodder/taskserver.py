

import json
import os
import subprocess
from typing import List

from taskserver.domain.entities.Task import Task


class TaskList():

    @staticmethod
    def discover(filename) -> List[Task]:
        try:
            pop = f"task -t {filename} --list-all --json".split(" ")
            res = subprocess.run(pop, stdout=subprocess.PIPE)
            raw = res.stdout.decode().strip()
            obj = json.loads(raw)
            list = obj.get("tasks", [])
            path = obj.get("location", "")
            base = os.path.dirname(path) if path else os.getcwd()
            return TaskList.parse(base, list)
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {filename}.')

    @staticmethod
    def parse(cwd, values):
        tasks = []
        for item in values:
            # Update and normalize paths for all tasks by stripping base folder prefix
            loc = item.get("location", {})
            path = loc.get("taskfile", '')
            path = path.removeprefix(cwd + "/")
            task = Task(
                file=path,
                key=item["name"],
                name=item["name"],
                desc=item["desc"],
                summary=item["summary"],
                vars={},
                sources=[],
                generates=[],
            )
            tasks.append(task)

        return tasks
