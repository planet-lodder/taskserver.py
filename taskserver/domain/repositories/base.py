
import json
import os

from abc import ABC, abstractmethod
import subprocess
from typing import Optional, Sequence

from taskserver.domain.entities.Task import Task
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import TaskfileConfig


class ATaskfileRepository(ABC):
    _nodes = None
    _taskfile = None
    _tasklist = None

    def __init__(self, filename: str):
        self._path = filename

    @property
    def taskfile(self) -> TaskfileConfig:
        if not self._taskfile:
            self._taskfile = self._load(self._path)  # Load and cache result
        return self._taskfile

    @property
    def nodes(self) -> TaskNode:
        if not self._nodes:
            self._nodes = TaskNode('', 'Task Actions')
            self._nodes.populate(self._list())
        return self._nodes

    def _load(self, path) -> TaskfileConfig:
        if os.path.exists(path):
            return TaskfileConfig.resolve(path)
        return {"_path": path}

    def _list(self):
        try:
            command = f"task -t {self._path} --list-all --json"
            pop = command.split(" ")
            res = subprocess.run(pop, stdout=subprocess.PIPE)
            raw = res.stdout.decode().strip()
            obj = json.loads(raw)
            self._tasklist = obj["tasks"] if "tasks" in obj else []
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {self._path}.')

        # Update and normalize paths for all tasks by stripping base folder prefix
        cwd = os.getcwd()
        for task in self._tasklist:
            # Update sub task location
            if "location" in task and "taskfile" in task["location"]:
                path = task["location"]["taskfile"]
                path = path.removeprefix(cwd + "/")
                task["location"]["taskfile"] = path

        return self._tasklist

    def listTasks(self):
        return self._tasklist

    def filterTasks(self, terms):
        def matches(key, vals, term):
            return key in vals and term.lower() in vals[key].lower()

        def search(task):
            if not terms:
                return True

            # Search for each work in the terms given
            match_all = True
            for term in terms.split(' '):
                found = False
                found = found or matches("name", task, term)
                found = found or matches("desc", task, term)
                found = found or matches("summary", task, term)
                match_all = match_all and found

            return match_all
        if len(terms):
            return list(filter(search, self._tasklist))
        return self._tasklist
